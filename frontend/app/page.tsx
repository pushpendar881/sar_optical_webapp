'use client'

import Link from 'next/link'
import { useLayoutEffect, useRef } from 'react'
import dynamic from 'next/dynamic'
import gsap from 'gsap'

const Scene = dynamic(() => import('@/components/Scene'), { ssr: false })

export default function LandingPage() {
  const scope = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'expo.out' } })

      tl.set('.hero-word', { yPercent: 110 })
        .set('.hero-fade', { opacity: 0, y: 12 })
        .set('.hero-canvas', { opacity: 0, scale: 0.9 })
        .to('.hero-canvas', { opacity: 1, scale: 1, duration: 1.6 }, 0.1)
        .to('.hero-word', { yPercent: 0, duration: 1.1, stagger: 0.08 }, 0.15)
        .to('.hero-fade', { opacity: 1, y: 0, duration: 0.9, stagger: 0.1 }, '-=0.5')
    }, scope)

    return () => ctx.revert()
  }, [])

  return (
    <main ref={scope} className="v0-landing">
      <div className="hero-canvas v0-canvas pointer-events-none">
        <div className="h-[70vh] w-[70vh] max-w-[90vw] mx-auto mt-[10vh]">
          <Scene />
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="v0-nav hero-fade">
        <div className="v0-nav-left">
          <div className="v0-logo">
            <span className="v0-logo-icon">⬡</span>
            <span className="v0-logo-text">SAR·OPTICAL</span>
          </div>
        </div>
        <div className="v0-nav-right">
          <a href="#paper" className="v0-nav-link">PAPER</a>
          <a href="#data" className="v0-nav-link">DATA</a>
          <a href="#about" className="v0-nav-link">ABOUT</a>
          <a href="#team" className="v0-nav-link">TEAM</a>
          <Link href="/demo" className="v0-nav-cta">
            DEMO
          </Link>
        </div>
      </nav>

      {/* Hero Content */}
      <section className="v0-hero">
        <div className="v0-hero-left">
          <div className="v0-label hero-fade">01 — INTELLIGENCE</div>
          <h1 className="v0-hero-title">
            <span className="v0-title-normal overflow-hidden block">
              <span className="hero-word block">ALL-WEATHER</span>
            </span>
            <span className="v0-title-italic overflow-hidden block">
              <span className="hero-word block">VISION</span>
            </span>
          </h1>
          <div className="v0-cta-wrapper hero-fade">
            <Link href="/demo" className="v0-cta-button">
              <span className="v0-cta-text">INITIALIZE</span>
              <span className="v0-cta-arrow">→</span>
            </Link>
            <div className="v0-scroll-indicator">
              <div className="v0-scroll-text">SCROLL</div>
              <div className="v0-scroll-line"></div>
            </div>
          </div>
        </div>

        <div className="v0-hero-right">
          <div className="v0-label-right hero-fade">02 — CRAFT</div>
          <h2 className="v0-hero-subtitle">
            <span className="v0-subtitle-normal overflow-hidden block">
              <span className="hero-word block">SAR TO OPTICAL</span>
            </span>
            <span className="v0-subtitle-italic overflow-hidden block">
              <span className="hero-word block">SYNTHESIS</span>
            </span>
          </h2>
          <div className="v0-specs hero-fade">
            <div className="v0-spec-item">
              <div className="v0-spec-label">RESOLUTION</div>
              <div className="v0-spec-value">256×256</div>
            </div>
            <div className="v0-spec-item">
              <div className="v0-spec-label">LATENCY</div>
              <div className="v0-spec-value">&lt;200ms</div>
            </div>
            <div className="v0-spec-item">
              <div className="v0-spec-label">DEVICE</div>
              <div className="v0-spec-value">CPU READY</div>
            </div>
          </div>
        </div>
      </section>

      {/* Paper Section */}
      <section className="v0-section v0-section-dark" id="paper">
        <div className="v0-section-header">
          <div className="v0-section-number">01</div>
          <div className="v0-section-title">RESEARCH PAPER</div>
        </div>
        
        <div className="v0-paper-content">
          <div className="v0-paper-card">
            <div className="v0-paper-badge">DRAFT</div>
            <h3 className="v0-paper-title">
              SAR to Optical Image Translation with Semantic Segmentation for Maritime Surveillance
            </h3>
            <p className="v0-paper-desc">
              Applied to International Conference on Machine Translation (ICMT). 
              This work presents a novel approach for translating Synthetic Aperture Radar (SAR) imagery 
              to optical domain using CycleGAN architecture with integrated semantic segmentation.
            </p>
            <div className="v0-paper-meta">
              <div className="v0-paper-meta-item">
                <span className="v0-paper-meta-label">STATUS</span>
                <span className="v0-paper-meta-value">Under Review</span>
              </div>
              <div className="v0-paper-meta-item">
                <span className="v0-paper-meta-label">CONFERENCE</span>
                <span className="v0-paper-meta-value">ICMT 2026</span>
              </div>
            </div>
            <a 
              href="#" 
              className="v0-paper-btn"
              onClick={(e) => { e.preventDefault(); alert('Paper draft coming soon! Currently under review at ICMT.'); }}
            >
              <span>VIEW DRAFT</span>
              <span className="v0-paper-arrow">→</span>
            </a>
          </div>
        </div>
      </section>

      {/* Data Contributions Section */}
      <section className="v0-section" id="data">
        <div className="v0-section-header">
          <div className="v0-section-number">02</div>
          <div className="v0-section-title">DATA CONTRIBUTIONS</div>
        </div>
        
        <div className="v0-data-grid">
          <a href="https://github.com/Swaraj1657/sar-optical-semantic-masks" target="_blank" rel="noopener noreferrer" className="v0-data-card">
            <div className="v0-data-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
              </svg>
            </div>
            <h3 className="v0-data-title">GitHub Repository</h3>
            <p className="v0-data-desc">
              Complete source code, training scripts, and semantic mask generation pipeline for SAR-Optical translation
            </p>
            <span className="v0-data-link">View Repository →</span>
          </a>

          <a href="https://figshare.com/articles/dataset/SAR_Optical_Dataset_with_Semantic_Masks/34335066" target="_blank" rel="noopener noreferrer" className="v0-data-card">
            <div className="v0-data-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </div>
            <h3 className="v0-data-title">Dataset Download</h3>
            <p className="v0-data-desc">
              Figshare hosted dataset with 5,000+ paired SAR-Optical images and semantic segmentation masks
            </p>
            <span className="v0-data-link">Download Dataset →</span>
          </a>

          <a href="https://certificates.theodi.org/datasets/6acb9e31b830b6ee9ba2ee65/certificates/6acb9e42b830b6ee9ba2ee6f" target="_blank" rel="noopener noreferrer" className="v0-data-card">
            <div className="v0-data-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
                <path d="M9 15h6"/>
                <path d="M9 12h6"/>
              </svg>
            </div>
            <h3 className="v0-data-title">ODI Certification</h3>
            <p className="v0-data-desc">
              Open Data Institute certified dataset ensuring quality, accessibility, and open licensing standards
            </p>
            <span className="v0-data-link">View Certificate →</span>
          </a>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="v0-section v0-section-dark" id="about">
        <div className="v0-section-header">
          <div className="v0-section-number">03</div>
          <div className="v0-section-title">CAPABILITIES</div>
        </div>
        
        <div className="v0-capabilities-grid">
          <div className="v0-capability">
            <div className="v0-capability-icon">⬡</div>
            <div className="v0-capability-title">CYCLEGAN TRANSLATION</div>
            <div className="v0-capability-desc">
              ResNet-9block architecture translates radar backscatter into RGB optical imagery without paired training data
            </div>
          </div>
          
          <div className="v0-capability">
            <div className="v0-capability-icon">⬢</div>
            <div className="v0-capability-title">SHIP DETECTION</div>
            <div className="v0-capability-desc">
              HRSID Faster R-CNN detector identifies maritime vessels on synthesized optical output with bounding boxes
            </div>
          </div>
          
          <div className="v0-capability">
            <div className="v0-capability-icon">⬣</div>
            <div className="v0-capability-title">EDGE DEPLOYMENT</div>
            <div className="v0-capability-desc">
              Optimized for CPU inference. Deploy on commodity hardware without CUDA requirements
            </div>
          </div>
          
          <div className="v0-capability">
            <div className="v0-capability-icon">⬡</div>
            <div className="v0-capability-title">MULTI-SENSOR</div>
            <div className="v0-capability-desc">
              Trained on TerraSAR-X, Gaofen-3, and Sentinel-1. Robust to sensor variations and polarization modes
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="v0-section" id="works">
        <div className="v0-section-header">
          <div className="v0-section-number">04</div>
          <div className="v0-section-title">APPLICATIONS</div>
        </div>
        
        <div className="v0-use-cases">
          <div className="v0-use-case">
            <div className="v0-use-case-number">01</div>
            <div className="v0-use-case-title">DEFENSE & INTELLIGENCE</div>
            <div className="v0-use-case-desc">All-weather maritime surveillance and asset tracking</div>
          </div>
          
          <div className="v0-use-case">
            <div className="v0-use-case-number">02</div>
            <div className="v0-use-case-title">PORT SECURITY</div>
            <div className="v0-use-case-desc">Real-time ship detection in harbors and traffic lanes</div>
          </div>
          
          <div className="v0-use-case">
            <div className="v0-use-case-number">03</div>
            <div className="v0-use-case-title">ENVIRONMENTAL</div>
            <div className="v0-use-case-desc">Monitor deforestation, flooding in cloud-covered regions</div>
          </div>
          
          <div className="v0-use-case">
            <div className="v0-use-case-number">04</div>
            <div className="v0-use-case-title">DISASTER RESPONSE</div>
            <div className="v0-use-case-desc">Assess structural damage when aerial access is impossible</div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="v0-section v0-section-dark" id="team">
        <div className="v0-section-header">
          <div className="v0-section-number">05</div>
          <div className="v0-section-title">RESEARCH TEAM</div>
        </div>
        
        <div className="v0-team-grid">
          <div className="v0-team-card">
            <div className="v0-team-avatar">PC</div>
            <h3 className="v0-team-name">Pushpendar Choudhary</h3>
            <p className="v0-team-role">Lead Researcher</p>
            <a href="mailto:2023.pushpendar.choudhary@ves.ac.in" className="v0-team-email">
              2023.pushpendar.choudhary@ves.ac.in
            </a>
          </div>

          <div className="v0-team-card">
            <div className="v0-team-avatar">SP</div>
            <h3 className="v0-team-name">Swaraj Pendare</h3>
            <p className="v0-team-role">ML Engineer</p>
            <a href="mailto:2023.swaraj.pendare@ves.ac.in" className="v0-team-email">
              2023.swaraj.pendare@ves.ac.in
            </a>
          </div>

          <div className="v0-team-card">
            <div className="v0-team-avatar">AS</div>
            <h3 className="v0-team-name">Aditya Santosh</h3>
            <p className="v0-team-role">Data Scientist</p>
            <a href="mailto:2023.aditya.santosh@ves.ac.in" className="v0-team-email">
              2023.aditya.santosh@ves.ac.in
            </a>
          </div>

          <div className="v0-team-card">
            <div className="v0-team-avatar">NG</div>
            <h3 className="v0-team-name">Nishant Gosavi</h3>
            <p className="v0-team-role">Research Engineer</p>
            <a href="mailto:2023.nishant.gosavi@ves.ac.in" className="v0-team-email">
              2023.nishant.gosavi@ves.ac.in
            </a>
          </div>

          <div className="v0-team-card v0-team-card-mentor">
            <div className="v0-team-avatar v0-team-avatar-mentor">AY</div>
            <h3 className="v0-team-name">Dr. Anjali Yeole</h3>
            <p className="v0-team-role">Faculty Mentor</p>
            <div className="v0-team-institution">Vivekanand Education Society</div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="v0-cta-section" id="contact">
        <div className="v0-cta-content">
          <div className="v0-cta-label">06 — INITIALIZE</div>
          <h2 className="v0-cta-title">
            <span className="v0-cta-title-normal">START</span>
            <span className="v0-cta-title-italic">TRANSLATING</span>
          </h2>
          <Link href="/demo" className="v0-cta-button-large">
            <span className="v0-cta-text">LAUNCH DEMO</span>
            <span className="v0-cta-arrow">→</span>
          </Link>
          <div className="v0-cta-note">NO SIGN-UP · CPU-OPTIMIZED · OPEN SOURCE</div>
        </div>
      </section>

      {/* Footer */}
      <footer className="v0-footer">
        <div className="v0-footer-grid">
          <div className="v0-footer-col">
            <div className="v0-footer-logo">
              <span className="v0-footer-logo-icon">⬡</span>
              SAR·OPTICAL
            </div>
            <p className="v0-footer-tagline">
              All-weather earth observation intelligence through synthetic aperture radar to optical image translation
            </p>
            <div className="v0-footer-institution">
              Vivekanand Education Society Institute of Technology
            </div>
          </div>

          <div className="v0-footer-col">
            <h4 className="v0-footer-heading">Navigation</h4>
            <a href="#paper" className="v0-footer-link">Research Paper</a>
            <a href="#data" className="v0-footer-link">Data Contributions</a>
            <a href="#about" className="v0-footer-link">Capabilities</a>
            <a href="#team" className="v0-footer-link">Team</a>
            <Link href="/demo" className="v0-footer-link">Demo</Link>
          </div>

          <div className="v0-footer-col">
            <h4 className="v0-footer-heading">Resources</h4>
            <a href="https://github.com/Swaraj1657/sar-optical-semantic-masks" target="_blank" rel="noopener noreferrer" className="v0-footer-link">
              GitHub Repository
            </a>
            <a href="https://figshare.com/articles/dataset/SAR_Optical_Dataset_with_Semantic_Masks/34335066" target="_blank" rel="noopener noreferrer" className="v0-footer-link">
              Dataset Download
            </a>
            <a href="https://certificates.theodi.org/datasets/6acb9e31b830b6ee9ba2ee65/certificates/6acb9e42b830b6ee9ba2ee6f" target="_blank" rel="noopener noreferrer" className="v0-footer-link">
              ODI Certificate
            </a>
          </div>

          <div className="v0-footer-col">
            <h4 className="v0-footer-heading">Connect</h4>
            <a href="mailto:2023.pushpendar.choudhary@ves.ac.in" className="v0-footer-link">Contact Team</a>
            <a href="https://github.com/Swaraj1657/sar-optical-semantic-masks" target="_blank" rel="noopener noreferrer" className="v0-footer-link">
              Star on GitHub
            </a>
          </div>
        </div>

        <div className="v0-footer-bottom">
          <div className="v0-footer-copyright">
            © 2026 SAR·OPTICAL Research Project. All rights reserved.
          </div>
          <div className="v0-footer-badges">
            <span className="v0-footer-badge">ICMT 2026</span>
            <span className="v0-footer-badge">ODI CERTIFIED</span>
            <span className="v0-footer-badge">OPEN SOURCE</span>
          </div>
        </div>
      </footer>
    </main>
  )
}
