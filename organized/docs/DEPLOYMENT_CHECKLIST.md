# SAR-to-Optical Web App - Deployment Checklist

## ✅ Files Required in Your Project Folder

Your `seg_cyclegan_project` folder should contain:
```
seg_cyclegan_project/
├── checkpoints/
│   ├── cyclegan_checkpoint_latest.pth    # Main checkpoint file
│   ├── eval_metrics_comparison.json     # Optional: evaluation metrics
│   └── *.pth                           # Any other checkpoint files
├── (other project files like dataset/, outputs/, etc.)
```

## ✅ System Requirements

### Python Dependencies (Auto-installed by setup)
- Python 3.8+
- PyTorch
- FastAPI
- uvicorn
- PIL/Pillow
- numpy

### Node.js Dependencies (Auto-installed by setup)  
- Node.js 18+
- npm or pnpm
- Next.js 16+
- React 19

## ✅ Quick Setup Commands

### Option 1: Automatic Setup (Windows)
```bash
setup.bat "C:\path\to\your\seg_cyclegan_project"
```

### Option 2: Automatic Setup (Linux/macOS)
```bash
chmod +x setup.sh
./setup.sh /path/to/your/seg_cyclegan_project
```

### Option 3: Python Script (Cross-platform)
```bash
python setup.py /path/to/your/seg_cyclegan_project
```

## ✅ What the Setup Does

1. **Copies Model Files**: Moves your `.pth` checkpoint files to `backend/data/checkpoints/`
2. **Creates Environment**: Sets up `backend/.env` with correct paths
3. **Installs Dependencies**: Runs `pip install -r requirements.txt` and `npm install`
4. **Starts Servers**: Launches both backend (port 8000) and frontend (port 3000)

## ✅ Directory Structure After Setup

```
sar_optical_webapp/
├── backend/
│   ├── data/
│   │   ├── checkpoints/          # ← Your model files go here
│   │   │   ├── cyclegan_checkpoint_latest.pth
│   │   │   └── eval_metrics_comparison.json
│   │   ├── uploads/              # ← Input SAR images
│   │   └── outputs/              # ← Generated optical images
│   ├── app.py                    # FastAPI server
│   ├── model.py                  # Model architecture
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # ← Auto-generated config
├── frontend/                     # Next.js React app
│   ├── app/
│   ├── components/
│   ├── package.json
│   └── node_modules/
├── setup.py                      # Setup script
├── setup.bat                     # Windows batch script
├── setup.sh                      # Unix shell script
└── SETUP_README.md               # Detailed instructions
```

## ✅ Environment Variables (Auto-configured)

The setup creates `backend/.env` with:
```env
CHECKPOINT_PATH=./backend/data/checkpoints/cyclegan_checkpoint_latest.pth
METRICS_JSON_PATH=./backend/data/checkpoints/eval_metrics_comparison.json
IMG_SIZE=256
DATA_DIR=./backend/data
```

## ✅ API Endpoints

The backend provides these endpoints:

- **POST** `/api/predict` - Upload SAR image and get optical conversion
- **GET** `/api/history` - Get previous conversions
- **GET** `/api/metrics` - Get model evaluation metrics
- **GET** `/api/model-info` - Get model information
- **GET** `/data/uploads/{filename}` - Serve uploaded images
- **GET** `/data/outputs/{filename}` - Serve generated images

## ✅ Frontend Features

- **Drag & Drop Upload**: Drop SAR images directly
- **Real-time Conversion**: See results immediately
- **Download Results**: Download generated optical images
- **Conversion History**: View previous conversions
- **Model Metrics**: Display evaluation metrics if available
- **Responsive Design**: Works on desktop and mobile

## ✅ Troubleshooting Guide

### Port Already in Use
```bash
# Backend on different port
cd backend
uvicorn app:app --host 0.0.0.0 --port 8001

# Frontend on different port  
cd frontend
PORT=3001 npm run dev
```

### CUDA/GPU Issues
- App auto-detects GPU availability
- Falls back to CPU if CUDA unavailable
- No manual configuration needed

### Checkpoint Not Found
- Ensure `.pth` files are in your project's `checkpoints/` folder
- Setup script looks for files with "latest" in name first
- Check console output to see which checkpoint was selected

### Dependencies Missing
```bash
# Manual Python install
pip install fastapi uvicorn torch pillow numpy

# Manual Node.js install
cd frontend && npm install
```

### CORS Issues
- Backend already configured with CORS enabled
- Frontend connects to `http://localhost:8000`
- If needed, modify `backendUrl` in `frontend/app/page.tsx`

## ✅ Testing the Setup

1. **Upload Test**: Try uploading a SAR image (.png or .jpg)
2. **Conversion Test**: Click "Run inference" and check for results
3. **Download Test**: Download the generated optical image
4. **History Test**: Check if conversions appear in history
5. **Metrics Test**: Verify metrics display (if eval_metrics_comparison.json exists)

## ✅ Performance Expectations

- **Image Size**: 256×256 pixels (configurable)
- **Inference Time**: 2-50ms depending on hardware
- **Memory Usage**: ~0.5GB VRAM (GPU) or ~1GB RAM (CPU)
- **File Formats**: Input (PNG/JPG), Output (PNG)

## ✅ Access URLs

After successful setup:
- 🌐 **Web App**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000  
- 📚 **API Docs**: http://localhost:8000/docs
- 📊 **Health Check**: http://localhost:8000/api/model-info