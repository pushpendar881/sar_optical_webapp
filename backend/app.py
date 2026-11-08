"""
FastAPI backend for the SAR -> Optical colorization demo.

Run:
    pip install -r requirements.txt
    export CHECKPOINT_PATH=/home/seg_cyclegan_project/checkpoints/cyclegan_checkpoint_latest.pth
    uvicorn app:app --host 0.0.0.0 --port 8000
"""
import os
import io
import json
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image

from detector import detect_and_overlay, detector_available, detector_error, load_detector
from detector_yolo import detect_and_overlay_yolo, yolo_detector_available, yolo_detector_error, load_yolo_detector
from model import load_generator

# ---------------- config ----------------
# Use relative paths that work on both Windows and Linux
CHECKPOINT_PATH = os.environ.get(
    "CHECKPOINT_PATH", "./data/checkpoints/cyclegan_checkpoint_latest_seg_model_optimize.pth"
)
METRICS_JSON_PATH = os.environ.get(
    "METRICS_JSON_PATH", "./data/checkpoints/eval_metrics_comparison.json"
)
IMG_SIZE = int(os.environ.get("IMG_SIZE", 256))
DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
DB_PATH = DATA_DIR / "history.db"

DEVICE = "cpu"  # Force CPU to match direct inference
print(f"DEBUG: Forcing CPU device to match direct inference")
G_AB = None  # loaded on startup
DETECTOR_READY = False
YOLO_DETECTOR_READY = False

# StaticFiles mounts below need these to exist at import time (before lifespan startup runs)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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
            inference_ms REAL NOT NULL,
            detected_filename TEXT,
            num_ships INTEGER,
            detection_info TEXT
        )
    """)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(predictions)")}
    if "detected_filename" not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN detected_filename TEXT")
    if "num_ships" not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN num_ships INTEGER")
    if "detection_info" not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN detection_info TEXT")
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global G_AB, DETECTOR_READY, YOLO_DETECTOR_READY
    init_db()
    print(f"DEBUG: Looking for checkpoint at: {CHECKPOINT_PATH}")
    print(f"DEBUG: Checkpoint exists: {Path(CHECKPOINT_PATH).exists()}")
    if Path(CHECKPOINT_PATH).exists():
        print(f"DEBUG: Checkpoint size: {Path(CHECKPOINT_PATH).stat().st_size} bytes")
    if not Path(CHECKPOINT_PATH).exists():
        raise RuntimeError(f"Checkpoint not found at {CHECKPOINT_PATH} -- set CHECKPOINT_PATH env var.")
    G_AB = load_generator(CHECKPOINT_PATH, DEVICE)
    print(f"Loaded generator from {CHECKPOINT_PATH} on {DEVICE}")
    
    # Try to load Detectron2 detector
    try:
        load_detector(DEVICE)
        DETECTOR_READY = True
        print("✓ Detectron2 (Faster R-CNN) detector loaded")
    except Exception as exc:
        DETECTOR_READY = False
        print(f"WARNING: Detectron2 detector not loaded ({exc})")
    
    # Try to load YOLOv8 detector
    try:
        load_yolo_detector(DEVICE)
        YOLO_DETECTOR_READY = True
        print("✓ YOLOv8 detector loaded")
    except Exception as exc:
        YOLO_DETECTOR_READY = False
        print(f"WARNING: YOLOv8 detector not loaded ({exc})")
    
    if not DETECTOR_READY and not YOLO_DETECTOR_READY:
        print("WARNING: No ship detectors available. Only colorization will work.")
    
    yield


app = FastAPI(title="SAR to Optical Colorization API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.post("/api/predict")
async def predict(
    file: UploadFile = File(...),
    confidence_threshold: float = Form(0.5),
    detector_type: str = Form("detectron2"),  # "detectron2" or "yolo"
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Upload an image file (png/jpg).")
    threshold = min(0.9, max(0.1, float(confidence_threshold)))

    raw = await file.read()
    try:
        sar_img = Image.open(io.BytesIO(raw)).convert("L").resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)
        print(f"DEBUG: Input image size: {sar_img.size}, mode: {sar_img.mode}")
    except Exception:
        raise HTTPException(400, "Could not read the uploaded file as an image.")

    pred_id = uuid.uuid4().hex[:12]
    input_filename = f"{pred_id}_input.png"
    output_filename = f"{pred_id}_output.png"
    detected_filename = f"{pred_id}_detected.png"
    sar_img.save(UPLOAD_DIR / input_filename)

    # Convert to tensor - match exactly with working inference script
    sar_array = np.array(sar_img, dtype=np.float32) / 127.5 - 1.0
    sar_t = torch.from_numpy(sar_array).unsqueeze(0).unsqueeze(0).to(DEVICE)  # [1, 1, H, W]
    print(f"DEBUG: Tensor shape: {sar_t.shape}, min: {sar_t.min():.3f}, max: {sar_t.max():.3f}")

    t0 = time.time()
    with torch.no_grad():
        fake_t = G_AB(sar_t)[0].permute(1, 2, 0).cpu().numpy()
        print(f"DEBUG: Output tensor shape: {fake_t.shape}, min: {fake_t.min():.3f}, max: {fake_t.max():.3f}")
        print(f"DEBUG: Channel means - R: {fake_t[:,:,0].mean():.3f}, G: {fake_t[:,:,1].mean():.3f}, B: {fake_t[:,:,2].mean():.3f}")

    fake_np = ((fake_t + 1) * 127.5).clip(0, 255).astype(np.uint8)
    print(f"DEBUG: Final image shape: {fake_np.shape}, min: {fake_np.min()}, max: {fake_np.max()}")
    print(f"DEBUG: Final channel means - R: {fake_np[:,:,0].mean():.1f}, G: {fake_np[:,:,1].mean():.1f}, B: {fake_np[:,:,2].mean():.1f}")

    out_img = Image.fromarray(fake_np)
    out_img.save(OUTPUT_DIR / output_filename)

    detections: list = []
    detection_info = "Ship detector is not loaded."
    detector_used = detector_type
    
    # Select detector based on type and availability
    if detector_type == "yolo" and yolo_detector_available():
        boxed_img, detections, detection_info = detect_and_overlay_yolo(sar_img, fake_np, threshold)
        boxed_img.save(OUTPUT_DIR / detected_filename)
        detector_used = "yolo"
    elif detector_type == "detectron2" and detector_available():
        boxed_img, detections, detection_info = detect_and_overlay(sar_img, fake_np, threshold)
        boxed_img.save(OUTPUT_DIR / detected_filename)
        detector_used = "detectron2"
    elif yolo_detector_available():
        # Fallback to YOLO if requested detector not available
        boxed_img, detections, detection_info = detect_and_overlay_yolo(sar_img, fake_np, threshold)
        boxed_img.save(OUTPUT_DIR / detected_filename)
        detector_used = "yolo"
        detection_info = "[Fallback to YOLOv8] " + detection_info
    elif detector_available():
        # Fallback to Detectron2 if YOLO not available
        boxed_img, detections, detection_info = detect_and_overlay(sar_img, fake_np, threshold)
        boxed_img.save(OUTPUT_DIR / detected_filename)
        detector_used = "detectron2"
        detection_info = "[Fallback to Detectron2] " + detection_info
    else:
        out_img.save(OUTPUT_DIR / detected_filename)
        err = detector_error() or yolo_detector_error()
        if err:
            detection_info = err

    inference_ms = (time.time() - t0) * 1000

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (id, timestamp, input_filename, output_filename, inference_ms, detected_filename, num_ships, detection_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            pred_id,
            time.strftime("%Y-%m-%d %H:%M:%S"),
            input_filename,
            output_filename,
            inference_ms,
            detected_filename,
            len(detections),
            detection_info,
        ),
    )
    conn.commit()
    conn.close()

    return {
        "id": pred_id,
        "input_url": f"/data/uploads/{input_filename}",
        "output_url": f"/data/outputs/{output_filename}",
        "detected_url": f"/data/outputs/{detected_filename}",
        "inference_ms": round(inference_ms, 1),
        "num_ships": len(detections),
        "detections": detections,
        "detection_info": detection_info,
        "detector_ready": detector_available() or yolo_detector_available(),
        "detector_used": detector_used,
        "confidence_threshold": threshold,
    }


@app.get("/api/history")
async def history(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        detected = r["detected_filename"] if "detected_filename" in r.keys() else None
        results.append(
            {
                "id": r["id"],
                "timestamp": r["timestamp"],
                "input_url": f"/data/uploads/{r['input_filename']}",
                "output_url": f"/data/outputs/{r['output_filename']}",
                "detected_url": f"/data/outputs/{detected}" if detected else None,
                "inference_ms": round(r["inference_ms"], 1),
                "num_ships": r["num_ships"] if "num_ships" in r.keys() else None,
                "detection_info": r["detection_info"] if "detection_info" in r.keys() else None,
            }
        )
    return results


@app.get("/api/metrics")
async def metrics():
    if not Path(METRICS_JSON_PATH).exists():
        return {"available": False}
    with open(METRICS_JSON_PATH) as f:
        data = json.load(f)
    return {"available": True, "checkpoint": CHECKPOINT_PATH, **data}


@app.get("/api/model-info")
async def model_info():
    return {
        "checkpoint": CHECKPOINT_PATH,
        "device": DEVICE,
        "img_size": IMG_SIZE,
        "architecture": "ResNet-9block CycleGAN generator (G_AB: SAR grayscale -> RGB optical)",
        "pipeline": "colorize → detect (HRSID detectors, boxes drawn on optical)",
        "detectron2_ready": DETECTOR_READY or detector_available(),
        "yolo_ready": YOLO_DETECTOR_READY or yolo_detector_available(),
        "detector_ready": (DETECTOR_READY or detector_available()) or (YOLO_DETECTOR_READY or yolo_detector_available()),
        "detectron2_error": detector_error(),
        "yolo_error": yolo_detector_error(),
    }


app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")


@app.get("/")
async def root():
    index_path = Path(__file__).parent.parent / "frontend" / "index.html"
    return FileResponse(index_path)


app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "frontend"), name="static")
