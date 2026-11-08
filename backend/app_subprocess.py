"""
FastAPI backend that uses subprocess to call the PyTorch inference script.
This avoids PyTorch DLL loading issues in the main process.
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
from fastapi.responses import FileResponse
from PIL import Image

# ---------------- config ----------------
CHECKPOINT_PATH = os.environ.get(
    "CHECKPOINT_PATH", "./data/checkpoints/cyclegan_checkpoint_latest.pth"
)
METRICS_JSON_PATH = os.environ.get(
    "METRICS_JSON_PATH", "./data/checkpoints/eval_metrics_comparison.json"
)
IMG_SIZE = int(os.environ.get("IMG_SIZE", 256))
DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
DB_PATH = DATA_DIR / "history.db"

# Use CPU inference script to avoid DLL issues
INFERENCE_SCRIPT = Path(__file__).parent.parent / "sar_to_optical_cpu.py"

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


def test_inference_script():
    """Test if the inference script works"""
    if not INFERENCE_SCRIPT.exists():
        print(f"⚠️  Inference script not found: {INFERENCE_SCRIPT}")
        return False
    
    if not Path(CHECKPOINT_PATH).exists():
        print(f"⚠️  Checkpoint not found: {CHECKPOINT_PATH}")
        return False
    
    print(f"✅ Inference script found: {INFERENCE_SCRIPT}")
    print(f"✅ Checkpoint found: {CHECKPOINT_PATH}")
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    if not test_inference_script():
        print("❌ Setup validation failed")
    else:
        print("🚀 Backend ready! Using subprocess inference to avoid DLL issues.")
    
    yield


app = FastAPI(title="SAR to Optical Colorization API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Upload an image file (png/jpg).")

    # Validate checkpoint exists
    if not Path(CHECKPOINT_PATH).exists():
        raise HTTPException(500, f"Model checkpoint not found: {CHECKPOINT_PATH}")

    raw = await file.read()
    try:
        sar_img = Image.open(io.BytesIO(raw)).convert("L").resize((IMG_SIZE, IMG_SIZE))
    except Exception:
        raise HTTPException(400, "Could not read the uploaded file as an image.")

    pred_id = uuid.uuid4().hex[:12]
    input_filename = f"{pred_id}_input.png"
    output_filename = f"{pred_id}_output.png"
    
    input_path = UPLOAD_DIR / input_filename
    output_path = OUTPUT_DIR / output_filename
    
    # Save input image
    sar_img.save(input_path)

    # Run inference via subprocess
    try:
        t0 = time.time()
        
        cmd = [
            sys.executable, str(INFERENCE_SCRIPT),
            "--sar", str(input_path),
            "--checkpoint", str(CHECKPOINT_PATH),
            "--output", str(output_path),
            "--img-size", str(IMG_SIZE)
        ]
        
        print(f"Running inference: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,  # 30 second timeout
            cwd=Path(__file__).parent.parent  # Run from project root
        )
        
        inference_ms = (time.time() - t0) * 1000
        
        if result.returncode != 0:
            print(f"Inference failed with code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            raise HTTPException(500, f"Inference failed: {result.stderr[:200]}")
        
        if not output_path.exists():
            raise HTTPException(500, "Inference completed but no output file generated")
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO predictions (id, timestamp, input_filename, output_filename, inference_ms) VALUES (?, ?, ?, ?, ?)",
            (pred_id, time.strftime("%Y-%m-%d %H:%M:%S"), input_filename, output_filename, inference_ms),
        )
        conn.commit()
        conn.close()

        print(f"✅ Inference completed in {inference_ms:.1f}ms")
        
        return {
            "id": pred_id,
            "input_url": f"/data/uploads/{input_filename}",
            "output_url": f"/data/outputs/{output_filename}",
            "inference_ms": round(inference_ms, 1),
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "Inference timed out after 30 seconds")
    except Exception as e:
        print(f"Inference error: {e}")
        raise HTTPException(500, f"Inference failed: {str(e)}")


@app.get("/api/history")
async def history(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
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
    except Exception as e:
        print(f"Error loading metrics: {e}")
        return {"available": False}


@app.get("/api/model-info")
async def model_info():
    return {
        "checkpoint": CHECKPOINT_PATH,
        "device": "cpu",  # Using CPU inference script
        "img_size": IMG_SIZE,
        "architecture": "ResNet-9block CycleGAN generator (G_AB: SAR grayscale -> RGB optical)",
        "inference_method": "subprocess",
    }


# Serve static files
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")


@app.get("/")
async def root():
    return {"message": "SAR to Optical Colorization API", "status": "ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)