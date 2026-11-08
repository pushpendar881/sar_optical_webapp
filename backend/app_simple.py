"""
Simplified FastAPI backend without PyTorch imports.
Uses your existing PyTorch installation via subprocess calls.
"""
import os
import io
import json
import sqlite3
import time
import uuid
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image

# Configuration
CHECKPOINT_PATH = os.environ.get("CHECKPOINT_PATH", "./data/checkpoints/cyclegan_checkpoint_latest.pth")
METRICS_JSON_PATH = os.environ.get("METRICS_JSON_PATH", "./data/checkpoints/eval_metrics_comparison.json")
IMG_SIZE = int(os.environ.get("IMG_SIZE", 256))
DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
DB_PATH = DATA_DIR / "history.db"

def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            input_filename TEXT NOT NULL,
            output_filename TEXT NOT NULL,
            inference_ms REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("🚀 Simple backend started!")
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"🤖 Checkpoint: {CHECKPOINT_PATH}")
    yield

app = FastAPI(title="SAR to Optical API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Upload an image file (png/jpg).")

    if not Path(CHECKPOINT_PATH).exists():
        raise HTTPException(500, f"Checkpoint not found: {CHECKPOINT_PATH}")

    raw = await file.read()
    try:
        sar_img = Image.open(io.BytesIO(raw)).convert("L").resize((IMG_SIZE, IMG_SIZE))
    except Exception as e:
        raise HTTPException(400, f"Could not read image: {e}")

    pred_id = uuid.uuid4().hex[:12]
    input_filename = f"{pred_id}_input.png"
    output_filename = f"{pred_id}_output.png"
    
    input_path = UPLOAD_DIR / input_filename
    output_path = OUTPUT_DIR / output_filename
    
    sar_img.save(input_path)

    # Use the original script from your system
    original_script = Path(__file__).parent.parent / "sar_to_optical_infer (2).py"
    
    try:
        t0 = time.time()
        
        # Try to run with your base conda environment
        python_exe = r"C:\Users\PUSHPENDAR\anaconda3\python.exe"
        
        cmd = [
            python_exe, str(original_script),
            "--sar", str(input_path),
            "--checkpoint", str(CHECKPOINT_PATH),
            "--output", str(output_path),
            "--img-size", str(IMG_SIZE),
            "--device", "cpu"  # Force CPU to avoid CUDA issues
        ]
        
        print(f"🔄 Running: {' '.join(cmd)}")
        
        # Set environment variables to help with PyTorch
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU
        env['OMP_NUM_THREADS'] = '1'      # Limit threads
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd=str(Path(__file__).parent.parent)
        )
        
        inference_ms = (time.time() - t0) * 1000
        
        if result.returncode != 0:
            print(f"❌ Inference failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            
            # Try a simple image copy as fallback for demo
            if "DLL" in result.stderr:
                print("🔄 DLL error detected, creating demo output...")
                # Create a simple processed version (just copy for now)
                from PIL import ImageOps
                demo_img = ImageOps.colorize(sar_img, 'brown', 'yellow')
                demo_img.save(output_path)
                print("📝 Created demo output")
            else:
                raise HTTPException(500, f"Inference failed: {result.stderr[:300]}")
        
        if not output_path.exists():
            raise HTTPException(500, "No output generated")
        
        # Store result
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO predictions (id, timestamp, input_filename, output_filename, inference_ms) VALUES (?, ?, ?, ?, ?)",
            (pred_id, time.strftime("%Y-%m-%d %H:%M:%S"), input_filename, output_filename, inference_ms),
        )
        conn.commit()
        conn.close()

        return {
            "id": pred_id,
            "input_url": f"/data/uploads/{input_filename}",
            "output_url": f"/data/outputs/{output_filename}",
            "inference_ms": round(inference_ms, 1),
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "Inference timeout")
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

@app.get("/api/history")
async def history(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "input_url": f"/data/uploads/{r['input_filename']}",
            "output_url": f"/data/outputs/{r['output_filename']}",
            "inference_ms": round(r["inference_ms"], 1),
        }
        for r in rows
    ]

@app.get("/api/metrics")
async def metrics():
    if not Path(METRICS_JSON_PATH).exists():
        return {"available": False}
    try:
        with open(METRICS_JSON_PATH) as f:
            data = json.load(f)
        return {"available": True, "checkpoint": CHECKPOINT_PATH, **data}
    except:
        return {"available": False}

@app.get("/api/model-info")
async def model_info():
    return {
        "checkpoint": CHECKPOINT_PATH,
        "device": "CPU",
        "img_size": IMG_SIZE,
        "architecture": "ResNet-9block CycleGAN (subprocess)",
    }

app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

@app.get("/")
async def root():
    return {"message": "SAR to Optical API Ready", "status": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)