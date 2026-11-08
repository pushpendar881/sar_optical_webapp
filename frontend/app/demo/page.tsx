'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  Check,
  Cpu,
  Download,
  FileImage,
  GitFork,
  Home,
  ImagePlus,
  LoaderCircle,
  RotateCcw,
  ScanSearch,
  Sparkles,
  Upload,
  X,
} from 'lucide-react'

type Run = {
  id: string
  name: string
  time: number
  size: string
  createdAt: string
  input_url?: string
  output_url?: string
  detected_url?: string
  num_ships?: number
}

type ApiResponse = {
  id: string
  input_url: string
  output_url: string
  detected_url?: string
  inference_ms: number
  num_ships?: number
  detection_info?: string
  detector_ready?: boolean
}

type ModelInfo = {
  checkpoint: string
  device: string
  img_size: number
  architecture: string
  pipeline?: string
  detector_ready?: boolean
  detector_error?: string | null
}

type Metrics = {
  available: boolean
  checkpoint?: string
  [key: string]: any
}

const formatBytes = (bytes: number) => {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function Page() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [inputUrl, setInputUrl] = useState('')
  const [outputUrl, setOutputUrl] = useState('')
  const [detectedUrl, setDetectedUrl] = useState('')
  const [detectionInfo, setDetectionInfo] = useState('')
  const [numShips, setNumShips] = useState<number | null>(null)
  const [threshold, setThreshold] = useState(0.5)
  const [detectorType, setDetectorType] = useState<'detectron2' | 'yolo'>('yolo')
  const [isDragging, setIsDragging] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [inferTime, setInferTime] = useState<number | null>(null)
  const [runs, setRuns] = useState<Run[]>([])
  const [outputReady, setOutputReady] = useState(false)
  const [error, setError] = useState('')
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [backendUrl] = useState(process.env.NODE_ENV === 'development' ? '' : 'http://localhost:8000')
  const [backendConnected, setBackendConnected] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem('sar-optical-runs')
      if (stored) setRuns(JSON.parse(stored))
    } catch {
      setRuns([])
    }
    
    // Load model info and metrics on startup
    loadModelInfo()
    loadMetrics()
    loadHistory()
    
    // Set up periodic retry for backend connection
    const retryInterval = setInterval(() => {
      if (!backendConnected && retryCount < 10) {
        setRetryCount(prev => prev + 1)
        checkBackendConnection()
      }
    }, 5000) // Try every 5 seconds
    
    return () => clearInterval(retryInterval)
  }, [])

  useEffect(() => {
    if (runs.length) window.localStorage.setItem('sar-optical-runs', JSON.stringify(runs))
  }, [runs])

  const checkBackendConnection = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/model-info`, {
        signal: AbortSignal.timeout(3000)
      })
      if (response.ok) {
        setBackendConnected(true)
        loadModelInfo()
        loadMetrics()
        loadHistory()
      }
    } catch (error) {
      setBackendConnected(false)
    }
  }

  const loadModelInfo = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/model-info`, {
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })
      if (response.ok) {
        const info = await response.json()
        setModelInfo(info)
        setBackendConnected(true)
      } else {
        console.warn('Backend not ready, model info unavailable')
        setBackendConnected(false)
      }
    } catch (error) {
      console.warn('Backend connection failed, using fallback data')
      setBackendConnected(false)
      // Set fallback model info
      setModelInfo({
        checkpoint: 'Loading...',
        device: 'unknown',
        img_size: 256,
        architecture: 'ResNet-9block CycleGAN'
      })
    }
  }

  const loadMetrics = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/metrics`, {
        signal: AbortSignal.timeout(5000)
      })
      if (response.ok) {
        const data = await response.json()
        setMetrics(data)
      } else {
        console.warn('Backend not ready, metrics unavailable')
      }
    } catch (error) {
      console.warn('Backend connection failed, metrics unavailable')
      setMetrics({ available: false })
    }
  }

  const loadHistory = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/history`, {
        signal: AbortSignal.timeout(5000)
      })
      if (response.ok) {
        const history = await response.json()
        const formattedHistory = history.map((item: any) => ({
          id: item.id,
          name: `prediction_${item.id}`,
          time: Math.round(item.inference_ms),
          size: 'Unknown',
          createdAt: item.timestamp,
          input_url: `${backendUrl}${item.input_url}`,
          output_url: `${backendUrl}${item.output_url}`,
          detected_url: item.detected_url ? `${backendUrl}${item.detected_url}` : undefined,
          num_ships: item.num_ships,
        }))
        setRuns(formattedHistory)
      }
    } catch (error) {
      console.warn('Backend connection failed, history unavailable')
      // Keep local storage history as fallback
    }
  }

  const handleFile = (file?: File) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setError('Please choose a PNG, JPG, or other image file.')
      return
    }
    setError('')
    setOutputReady(false)
    setInferTime(null)
    setDetectedUrl('')
    setDetectionInfo('')
    setNumShips(null)
    setSelectedFile(file)
    setInputUrl((previous) => {
      if (previous) URL.revokeObjectURL(previous)
      return URL.createObjectURL(file)
    })
  }

  const runInference = async () => {
    if (!selectedFile || isRunning) return
    
    if (!backendConnected) {
      setError('Backend API is not available. Please start the backend server.')
      return
    }
    
    setError('')
    setIsRunning(true)
    setOutputReady(false)
    setOutputUrl('')
    setDetectedUrl('')
    setDetectionInfo('')
    setNumShips(null)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('confidence_threshold', String(threshold))
      formData.append('detector_type', detectorType)
      
      const started = performance.now()
      const response = await fetch(`${backendUrl}/api/predict`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Prediction failed')
      }
      
      const result: ApiResponse = await response.json()
      const elapsed = performance.now() - started
      
      setInferTime(Math.round(elapsed))
      setOutputUrl(`${backendUrl}${result.output_url}`)
      setDetectedUrl(result.detected_url ? `${backendUrl}${result.detected_url}` : '')
      setDetectionInfo(result.detection_info || '')
      setNumShips(typeof result.num_ships === 'number' ? result.num_ships : null)
      setOutputReady(true)
      
      // Add to runs
      const newRun: Run = {
        id: result.id,
        name: selectedFile.name,
        time: Math.round(result.inference_ms),
        size: formatBytes(selectedFile.size),
        createdAt: new Date().toISOString(),
        input_url: `${backendUrl}${result.input_url}`,
        output_url: `${backendUrl}${result.output_url}`,
        detected_url: result.detected_url ? `${backendUrl}${result.detected_url}` : undefined,
        num_ships: result.num_ships,
      }
      
      setRuns((current) => [newRun, ...current].slice(0, 8))
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Prediction failed')
    } finally {
      setIsRunning(false)
    }
  }

  const clearRun = () => {
    if (inputUrl) URL.revokeObjectURL(inputUrl)
    setSelectedFile(null)
    setInputUrl('')
    setOutputUrl('')
    setDetectedUrl('')
    setDetectionInfo('')
    setNumShips(null)
    setOutputReady(false)
    setInferTime(null)
    setError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const downloadImage = (url: string, prefix: string) => {
    if (!url) return
    const link = document.createElement('a')
    link.href = url
    link.download = `${prefix}_${selectedFile?.name || 'output'}.png`
    link.click()
  }

  const renderMetrics = () => {
    if (!metrics?.available) {
      return [
        ['PSNR', '—', 'dB'],
        ['SSIM', '—', ''],
        ['LPIPS', '—', ''],
        ['MACE', '—', ''],
        ['FID', '—', ''],
      ]
    }
    
    // Use QXS-SAROPT (in-distribution) or SAR2Opt (held-out) metrics
    // Prefer SAR2Opt for more realistic generalization metrics
    const modelData = metrics['SAR2Opt'] || metrics['QXS-SAROPT'] || {}
    
    return [
      ['PSNR', modelData.PSNR ? modelData.PSNR.toFixed(2) : '—', 'dB'],
      ['SSIM', modelData.SSIM ? modelData.SSIM.toFixed(4) : '—', ''],
      ['LPIPS', modelData.LPIPS ? modelData.LPIPS.toFixed(4) : '—', ''],
      ['MACE', modelData.MACE ? modelData.MACE.toFixed(4) : '—', ''],
      ['FID', modelData.FID ? modelData.FID.toFixed(1) : '—', ''],
    ]
  }

  const getMetricStatus = (metric: string, value: string) => {
    if (value === '—') return 'N/A'
    
    const numValue = parseFloat(value)
    switch (metric) {
      case 'PSNR':
        return numValue > 25.0 ? 'GOOD' : numValue > 15.0 ? 'FAIR' : 'POOR'
      case 'SSIM':
        return numValue > 0.8 ? 'GOOD' : numValue > 0.5 ? 'FAIR' : 'POOR'
      case 'LPIPS':
        return numValue < 0.2 ? 'GOOD' : numValue < 0.5 ? 'FAIR' : 'POOR'
      case 'MACE':
        return numValue < 5.0 ? 'GOOD' : numValue < 20.0 ? 'FAIR' : 'POOR'
      case 'FID':
        return numValue < 50.0 ? 'GOOD' : numValue < 100.0 ? 'FAIR' : 'POOR'
      default:
        return 'PASS'
    }
  }

  const getMetricReference = (metric: string) => {
    switch (metric) {
      case 'PSNR': return '> 25.0 dB (good), > 15.0 dB (fair)'
      case 'SSIM': return '> 0.8 (good), > 0.5 (fair)'
      case 'LPIPS': return '< 0.2 (good), < 0.5 (fair)'
      case 'MACE': return '< 5.0 (good), < 20.0 (fair)'
      case 'FID': return '< 50 (good), < 100 (fair)'
      default: return 'within range'
    }
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="site-header">
        <div className="brand" aria-label="SAR to Optical">
          <Link href="/" className="home-link" aria-label="Back to home">
            <Home size={18} />
          </Link>
          <span className="brand-word brand-sar">SAR</span>
          <ArrowRight className="brand-arrow" aria-hidden="true" />
          <span className="brand-word brand-optical">Optical</span>
        </div>
        <div className="header-actions">
          <Link href="/" className="back-to-home-btn">
            <ArrowLeft size={16} />
            <span>Back to Home</span>
          </Link>
          <div className="connection-status">
            <span className={`status-indicator ${backendConnected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot" />
              {backendConnected ? 'API Connected' : 'API Disconnected'}
            </span>
            {!backendConnected && (
              <button className="retry-btn" onClick={checkBackendConnection}>
                Retry
              </button>
            )}
          </div>
          <span className="model-badge">
            <span className="status-dot" /> 
            {modelInfo ? `${modelInfo.device.toUpperCase()} · ${modelInfo.architecture.split(' ')[0]}` : 'Loading...'}
          </span>
          <a className="icon-link" href="https://github.com/Swaraj1657/sar-optical-semantic-masks" target="_blank" rel="noreferrer" aria-label="Open GitHub"><GitFork size={17} /></a>
        </div>
      </header>

      <div className="workspace">
        <section className="intro-row">
          <div>
            <p className="eyebrow"><Activity size={14} /> FRONTEND INFERENCE LAB</p>
            <h1>Translate radar into <span>daylight.</span></h1>
            <p className="lede">A local-first workspace for SAR-to-optical translation, then HRSID ship detection. Drop a radar capture to colorize it and overlay ship boxes on the optical scene.</p>
          </div>
          <div className="intro-specs" aria-label="Model specifications">
            <div><span>MODEL</span><strong>{modelInfo?.architecture.split(' ')[0] || 'Loading...'}</strong></div>
            <div><span>INPUT</span><strong>{modelInfo?.img_size || 256} × {modelInfo?.img_size || 256}</strong></div>
            <div><span>MODE</span><strong>LIVE API</strong></div>
          </div>
        </section>

        <section className="demo-grid" aria-label="Image translation workspace">
          <article className="panel input-panel">
            <div className="panel-heading">
              <div><p className="panel-kicker">01 / SOURCE</p><h2>SAR Input</h2></div>
              {selectedFile && <button className="quiet-button" onClick={clearRun} aria-label="Clear selected image"><X size={16} /></button>}
            </div>
            <div
              className={`image-frame ${isDragging ? 'dragging' : ''}`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(event) => { event.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(event) => { event.preventDefault(); setIsDragging(false); handleFile(event.dataTransfer.files[0]) }}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') inputRef.current?.click() }}
              aria-label="Upload a SAR image"
            >
              {inputUrl ? <img src={inputUrl} alt="Selected SAR source" className="source-preview" /> : <div className="upload-placeholder"><ImagePlus size={34} /><strong>Click or drop a SAR image</strong><span>PNG, JPG · max 25 MB</span></div>}
              <div className="frame-corner frame-corner-tl" /><div className="frame-corner frame-corner-tr" /><div className="frame-corner frame-corner-bl" /><div className="frame-corner frame-corner-br" />
              {isRunning && <div className="scan-line" />}
            </div>
            <input ref={inputRef} type="file" accept="image/png,image/jpeg,image/webp" className="sr-only" onChange={(event) => handleFile(event.target.files?.[0])} />
            <div className="file-meta">{selectedFile ? <><span><FileImage size={14} /> {selectedFile.name}</span><span>{formatBytes(selectedFile.size)}</span></> : <span>Awaiting source data</span>}</div>
            
            <div className="detector-toggle">
              <label className="toggle-label">Ship Detector:</label>
              <div className="toggle-buttons">
                <button
                  type="button"
                  className={`toggle-btn ${detectorType === 'detectron2' ? 'active' : ''}`}
                  onClick={() => setDetectorType('detectron2')}
                  disabled={isRunning}
                >
                  <span className="toggle-icon">🎯</span>
                  Detectron2
                </button>
                <button
                  type="button"
                  className={`toggle-btn ${detectorType === 'yolo' ? 'active' : ''}`}
                  onClick={() => setDetectorType('yolo')}
                  disabled={isRunning}
                >
                  <span className="toggle-icon">⚡</span>
                  YOLOv8
                </button>
              </div>
            </div>
            
            <label className="threshold-row">
              <span>Confidence {threshold.toFixed(2)}</span>
              <input
                type="range"
                min={0.1}
                max={0.9}
                step={0.05}
                value={threshold}
                onChange={(event) => setThreshold(parseFloat(event.target.value))}
                disabled={isRunning}
              />
            </label>
            {error && <p className="error-message" role="alert">{error}</p>}
            <button className="run-button" disabled={!selectedFile || isRunning} onClick={runInference}>{isRunning ? <><LoaderCircle className="spin" size={17} /> Running pipeline…</> : <><Sparkles size={17} /> Colorize &amp; detect</>}</button>
          </article>

          <article className="panel output-panel">
            <div className="panel-heading">
              <div><p className="panel-kicker">02 / SYNTHESIS</p><h2>Generated Optical</h2></div>
              <div className="output-actions">
                <span className={`output-status ${outputReady ? 'ready' : ''}`}>
                  {outputReady ? <><Check size={13} /> READY</> : 'STANDBY'}
                </span>
                {outputReady && (
                  <button className="icon-button" onClick={() => downloadImage(outputUrl, 'optical')} aria-label="Download colorized result">
                    <Download size={16} />
                  </button>
                )}
              </div>
            </div>
            <div className={`image-frame output-frame ${outputReady ? 'has-output' : ''}`}>
              {outputReady && outputUrl ? 
                <img src={outputUrl} alt="Generated optical result" className="output-preview" /> : 
                <div className="output-placeholder">
                  <div className="placeholder-mark"><Cpu size={24} /></div>
                  <span>{isRunning ? 'Synthesizing scene…' : 'Output will appear here'}</span>
                  <small>{isRunning ? 'Neural translation in progress' : 'Run inference to generate a result'}</small>
                </div>
              }
              {isRunning && <div className="scan-line" />}
              <div className="frame-corner frame-corner-tl" /><div className="frame-corner frame-corner-tr" /><div className="frame-corner frame-corner-bl" /><div className="frame-corner frame-corner-br" />
            </div>
            <div className="output-meta"><span>INFERENCE TIME</span><strong>{inferTime ? `${inferTime} ms` : '—'}</strong></div>
          </article>

          <article className="panel output-panel">
            <div className="panel-heading">
              <div><p className="panel-kicker">03 / DETECT</p><h2>Ships on Optical</h2></div>
              <div className="output-actions">
                <span className={`output-status ${outputReady ? 'ready' : ''}`}>
                  {outputReady ? <><Check size={13} /> {numShips == null ? 'READY' : `${numShips} SHIP${numShips === 1 ? '' : 'S'}`}</> : 'STANDBY'}
                </span>
                {outputReady && detectedUrl && (
                  <button className="icon-button" onClick={() => downloadImage(detectedUrl, 'detected')} aria-label="Download detection result">
                    <Download size={16} />
                  </button>
                )}
              </div>
            </div>
            <div className={`image-frame output-frame ${outputReady ? 'has-output' : ''}`}>
              {outputReady && detectedUrl ?
                <img src={detectedUrl} alt="Ships detected on colorized optical image" className="output-preview" /> :
                <div className="output-placeholder">
                  <div className="placeholder-mark"><ScanSearch size={24} /></div>
                  <span>{isRunning ? 'Detecting ships…' : 'Boxes will appear here'}</span>
                  <small>{isRunning ? 'HRSID Faster R-CNN on aligned SAR' : 'Run the pipeline to overlay detections'}</small>
                </div>
              }
              {isRunning && <div className="scan-line" />}
              <div className="frame-corner frame-corner-tl" /><div className="frame-corner frame-corner-tr" /><div className="frame-corner frame-corner-bl" /><div className="frame-corner frame-corner-br" />
            </div>
            <pre className="detection-info">{detectionInfo || 'Detection summary will appear here'}</pre>
          </article>
        </section>

        <section className="panel metrics-panel">
          <div className="section-heading">
            <div><p className="panel-kicker">04 / VALIDATION</p><h2>Evaluation metrics</h2></div>
            <span className="metrics-note">
              {metrics?.available ? 
                `LIVE DATA · ${metrics['SAR2Opt'] ? 'SAR2OPT (HELD-OUT)' : 'QXS-SAROPT'}` : 
                'NO DATA'
              } · {modelInfo?.checkpoint?.split('/').pop() || 'MODEL'}
            </span>
          </div>
          <div className="metrics-table" role="table" aria-label="Evaluation metrics">
            <div className="metric-row metric-header" role="row">
              <span>METRIC</span><span>VALUE</span><span>REFERENCE</span><span>STATUS</span>
            </div>
            {renderMetrics().map(([label, value, unit]) => {
              const status = getMetricStatus(label, value);
              return (
                <div className="metric-row" role="row" key={label}>
                  <span className="metric-name">{label}</span>
                  <strong>{value} <small>{unit}</small></strong>
                  <span className="metric-reference">
                    {getMetricReference(label)}
                  </span>
                  <span className={`metric-status status-${status.toLowerCase()}`}>
                    <span className="status-dot" /> 
                    {status}
                  </span>
                </div>
              )
            })}
          </div>
          {metrics?.available && (
            <div className="metrics-footer">
              <p className="metrics-info">
                <strong>Dataset Info:</strong> {metrics['SAR2Opt'] ? 
                  '2077 samples, held-out evaluation (TerraSAR-X vs Gaofen-3)' : 
                  '2077 samples, in-distribution evaluation'
                }
              </p>
              {metrics['SAR2Opt'] && (
                <p className="metrics-note-small">
                  SAR2Opt provides genuine generalization signal - urban Google Earth optical at ~1m GSD
                </p>
              )}
            </div>
          )}
        </section>

        <section className="panel history-panel">
          <div className="section-heading">
            <div><p className="panel-kicker">05 / WORKSPACE</p><h2>Recent runs</h2></div>
            <button className="text-button" onClick={() => setRuns([])} disabled={!runs.length}>
              <RotateCcw size={14} /> Clear history
            </button>
          </div>
          {runs.length ? (
            <div className="history-strip">
              {runs.map((run) => (
                <div 
                  className="history-item" 
                  key={run.id}
                  onClick={() => run.output_url && window.open(run.output_url, '_blank')}
                  style={{ cursor: run.output_url ? 'pointer' : 'default' }}
                >
                  <div className="history-thumb">
                    <div className="thumb-radar" />
                    <div className="thumb-light" />
                  </div>
                  <div>
                    <strong>{run.name}</strong>
                    <span>{run.size} · {run.time} ms{typeof run.num_ships === 'number' ? ` · ${run.num_ships} ships` : ''}</span>
                  </div>
                  <Download size={15} />
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-history">
              <Upload size={16} /> Your completed translations will appear here.
            </div>
          )}
        </section>
      </div>

      <footer><span>SAR → OPTICAL</span><span>LOCAL-FIRST IMAGE TRANSLATION</span><span>BUILD 0.1.0</span></footer>
    </main>
  )
}
