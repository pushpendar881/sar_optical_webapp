# 🛰️ SAR-to-Optical Web App

Transform SAR (Synthetic Aperture Radar) images into colorized optical images using your trained CycleGAN model in a beautiful web interface.

## 🚀 Quick Start (Easiest)

### Option 1: Drag & Drop (Windows)
1. **Drag** your `seg_cyclegan_project` folder 
2. **Drop** it onto `DRAG_AND_DROP_YOUR_PROJECT_HERE.bat`
3. **Wait** for automatic setup and launch!

### Option 2: One-Click Deploy (All platforms)
```bash
python deploy.py /path/to/your/seg_cyclegan_project
```

### Option 3: Windows Batch
```bash
setup.bat "C:\path\to\your\seg_cyclegan_project"
```

### Option 4: Unix/Linux/macOS
```bash
./setup.sh /path/to/your/seg_cyclegan_project
```

## 📊 Your Model Performance

Based on your evaluation results:

| Metric | QXS-SAROPT (In-dist) | SAR2Opt (Held-out) | Reference |
|--------|-----------------------|---------------------|-----------|
| **PSNR** | 17.44 dB | 13.29 dB | > 15.0 dB (fair) |
| **SSIM** | 0.3332 | 0.2080 | > 0.5 (fair) |
| **LPIPS** | 0.5303 | 0.6768 | < 0.5 (fair) |
| **MACE** | 6.44 | 32.25 | < 20.0 (fair) |
| **FID** | 118.95 | 180.18 | < 100 (fair) |

**Dataset**: 2077 samples, SAR2Opt provides genuine generalization (TerraSAR-X vs Gaofen-3)

## ✨ Features

- 📤 **Drag & Drop Upload**: Easy SAR image uploading
- 🎨 **Real-time Conversion**: Fast SAR to optical translation  
- 📊 **Live Metrics**: Your actual evaluation metrics displayed
- 📜 **History**: View and download previous conversions
- 💾 **Downloads**: Get generated optical images
- 🔧 **Model Info**: View architecture and performance details
- 🌐 **Web Interface**: Modern, responsive UI
- 🔥 **GPU/CPU Support**: Automatic hardware detection

## 🌐 Access URLs

- **Web App**: http://localhost:3000
- **API Backend**: http://localhost:8000  
- **API Docs**: http://localhost:8000/docs

## 🛠️ Manual Setup (Advanced)

### 1. Copy Project Files
```bash
mkdir -p backend/data/checkpoints
cp /your/project/checkpoints/*.pth backend/data/checkpoints/
cp /your/project/checkpoints/eval_metrics_comparison.json backend/data/checkpoints/
```

### 2. Configure Environment
Create `backend/.env`:
```env
CHECKPOINT_PATH=./backend/data/checkpoints/cyclegan_checkpoint_latest.pth
METRICS_JSON_PATH=./backend/data/checkpoints/eval_metrics_comparison.json
IMG_SIZE=256
DATA_DIR=./backend/data
```

### 3. Install Dependencies
```bash
# Backend
cd backend
pip install fastapi uvicorn torch torchvision pillow numpy python-multipart

# Frontend  
cd ../frontend
npm install
```

### 4. Start Servers
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 📁 Project Structure After Setup

```
sar_optical_webapp/
├── backend/
│   ├── data/
│   │   ├── checkpoints/          # Your .pth model files
│   │   │   ├── cyclegan_checkpoint_latest.pth
│   │   │   └── eval_metrics_comparison.json
│   │   ├── uploads/              # Uploaded SAR images
│   │   └── outputs/              # Generated optical images
│   ├── app.py                    # FastAPI server
│   ├── model.py                  # ResNet CycleGAN architecture
│   └── requirements.txt
├── frontend/                     # Next.js React app
├── deploy.py                     # One-click deployment
├── setup.py                      # Setup script  
└── DRAG_AND_DROP_YOUR_PROJECT_HERE.bat
```

## 🔧 Troubleshooting

### Dependencies Missing
```bash
# Check what's missing
python deploy.py --check-only /path/to/project

# Install Python deps
pip install fastapi uvicorn torch pillow numpy

# Install Node.js from: https://nodejs.org/
```

### Checkpoint Not Found
- Ensure `.pth` files are in your project directory
- Script looks for files with "latest", "cyclegan", or "G_AB" in name
- Check console output to see which checkpoint was selected

### Port Already in Use  
```bash
# Use different ports
uvicorn app:app --port 8001  # Backend
PORT=3001 npm run dev        # Frontend
```

### GPU Issues
- App auto-detects GPU/CPU
- Works on both CUDA and CPU
- Check model info in web interface for current device

## 🎯 Supported Formats

- **Input**: PNG, JPG, JPEG (grayscale SAR images)
- **Output**: PNG (colorized optical images)  
- **Size**: 256×256 pixels (configurable via IMG_SIZE)

## ⚡ Performance

- **Inference**: ~2-3ms (your model's actual performance)
- **Memory**: ~0.46GB GPU memory
- **Throughput**: Real-time processing
- **Quality**: PSNR 13-17dB, FID 119-180

## 🎮 Usage

1. **Open** http://localhost:3000
2. **Upload** a SAR image (drag & drop or click)
3. **Click** "Run inference" 
4. **View** the generated optical image
5. **Download** your results
6. **Check** metrics and history

Your model is now ready to transform radar imagery into beautiful optical scenes! 🛰️→🌍