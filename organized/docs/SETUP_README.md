# SAR-to-Optical Web App Setup

This guide helps you quickly set up and run the SAR-to-Optical image conversion web application with your trained model.

## Quick Start

### Option 1: Windows Batch Script (Easiest)
```bash
# Double-click setup.bat or run in Command Prompt:
setup.bat "C:\path\to\your\seg_cyclegan_project"
```

### Option 2: Python Script (Cross-platform)
```bash
python setup.py /path/to/your/seg_cyclegan_project
```

### Option 3: Manual Setup

1. **Copy your project files**:
   ```bash
   # Copy checkpoint files to backend/data/checkpoints/
   mkdir -p backend/data/checkpoints
   cp /your/project/checkpoints/*.pth backend/data/checkpoints/
   cp /your/project/checkpoints/eval_metrics_comparison.json backend/data/checkpoints/ (if available)
   ```

2. **Set environment variables** (create `backend/.env`):
   ```env
   CHECKPOINT_PATH=./backend/data/checkpoints/cyclegan_checkpoint_latest.pth
   METRICS_JSON_PATH=./backend/data/checkpoints/eval_metrics_comparison.json
   IMG_SIZE=256
   DATA_DIR=./backend/data
   ```

3. **Install dependencies**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

4. **Start servers**:
   ```bash
   # Terminal 1: Backend
   cd backend
   python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## Access the Application

- 🌐 **Web Interface**: http://localhost:3000
- 🔧 **API Backend**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs

## Project Structure After Setup

```
sar_optical_webapp/
├── backend/
│   ├── data/
│   │   ├── checkpoints/          # Your model files
│   │   ├── uploads/              # Uploaded SAR images
│   │   └── outputs/              # Generated optical images
│   ├── app.py                    # FastAPI backend
│   ├── model.py                  # Model architecture
│   └── requirements.txt
├── frontend/                     # Next.js React app
├── setup.py                     # Setup script
└── setup.bat                    # Windows batch script
```

## Troubleshooting

### Run Setup Verification
```bash
# After setup, test everything is working
python test_setup.py
```

### Dependencies Not Found
```bash
# Install Python dependencies
pip install fastapi uvicorn torch torchvision pillow numpy

# Install Node.js dependencies
cd frontend && npm install
```

### Checkpoint Not Found
- Make sure your checkpoint files (`.pth`) are in your project directory
- The script looks for files containing "latest" in the name first
- Check the console output to see which checkpoint was selected

### Port Already in Use
```bash
# Use different ports
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8001

cd frontend
PORT=3001 npm run dev
```

### GPU/CUDA Issues
The app automatically detects and uses GPU if available, but falls back to CPU. For CPU-only inference, no additional setup is needed.

## Features

- 📤 **Upload SAR Images**: Drag and drop or click to upload
- 🎨 **Real-time Conversion**: SAR to optical image colorization
- 📊 **Model Metrics**: View evaluation metrics if available
- 📜 **Conversion History**: See previous conversions
- 💾 **Download Results**: Download generated optical images
- 🔧 **Model Information**: View model architecture and device info

## Supported File Formats

- **Input**: PNG, JPG, JPEG (grayscale SAR images)
- **Output**: PNG (colorized optical images)

## Performance

- **Image Size**: 256x256 pixels (configurable via IMG_SIZE env variable)
- **Inference Time**: ~2-50ms depending on hardware
- **GPU Memory**: ~0.5GB VRAM when using GPU