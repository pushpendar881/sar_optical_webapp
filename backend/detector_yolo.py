"""YOLOv8 HRSID ship detector.

Detects on the SAR image and draws boxes onto the colorized optical image.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

YOLO_WEIGHTS_PATH = os.getenv(
    "YOLO_WEIGHTS_PATH", 
    str(Path(__file__).parent.parent / "runs" / "yolov8m_hrsid" / "weights" / "best.pt")
)

_model = None
_load_error: str | None = None


def load_yolo_detector(device: str = "cpu"):
    """Load YOLOv8 model. Safe to call more than once."""
    global _model, _load_error
    if _model is not None:
        return _model
    if _load_error:
        raise RuntimeError(_load_error)

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        _load_error = (
            "YOLOv8 is not installed. Install with: "
            "pip install ultralytics"
        )
        raise RuntimeError(_load_error) from exc

    if not Path(YOLO_WEIGHTS_PATH).exists():
        _load_error = f"YOLOv8 weights not found at {YOLO_WEIGHTS_PATH}"
        raise RuntimeError(_load_error)

    print(f"Loading YOLOv8 detector from {YOLO_WEIGHTS_PATH}...")
    _model = YOLO(YOLO_WEIGHTS_PATH)
    _model.to(device)
    print(f"YOLOv8 detector loaded on {device}")
    return _model


def yolo_detector_available() -> bool:
    return _model is not None


def yolo_detector_error() -> str | None:
    return _load_error


def _font():
    try:
        return ImageFont.truetype("Helvetica.ttc", 12)
    except OSError:
        return ImageFont.load_default()


def detect_and_overlay_yolo(
    sar_image: Image.Image,
    colorized_rgb: np.ndarray,
    confidence_threshold: float = 0.5,
) -> tuple[Image.Image, list[dict], str]:
    """Run YOLOv8 detection on SAR and overlay boxes on the colorized RGB array."""
    if _model is None:
        raise RuntimeError(_load_error or "YOLOv8 detector is not loaded.")

    h, w = colorized_rgb.shape[:2]
    # Convert SAR image to RGB for YOLO
    sar_rgb = sar_image.convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
    
    # Run inference
    results = _model(sar_rgb, conf=confidence_threshold, verbose=False)
    
    detections: list[dict] = []
    if len(results) > 0 and results[0].boxes is not None:
        boxes = results[0].boxes
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            detections.append({
                "id": i + 1,
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "score": round(conf, 4)
            })

    # Draw boxes on colorized image
    boxed = Image.fromarray(colorized_rgb.copy())
    draw = ImageDraw.Draw(boxed)
    font = _font()
    
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        # Draw box with YOLOv8 green color
        draw.rectangle([x1, y1, x2, y2], outline=(34, 139, 34), width=2)
        label = f"ship {det['score']:.2f}"
        ty = max(0, y1 - 14)
        draw.rectangle([x1, ty, x1 + 78, ty + 14], fill=(34, 139, 34))
        draw.text((x1 + 4, ty + 1), label, fill=(255, 255, 255), font=font)

    num = len(detections)
    info = f"[YOLOv8] Detected {num} ship(s)"
    if detections:
        info += "\nConfidence scores: " + ", ".join(f"{d['score']:.2f}" for d in detections)
        info += "\n\nBounding boxes (x1,y1,x2,y2):\n"
        info += "\n".join(
            f"  Ship {d['id']}: [{d['bbox'][0]},{d['bbox'][1]},{d['bbox'][2]},{d['bbox'][3]}]  conf={d['score']:.2f}"
            for d in detections
        )
    else:
        info += "\nNo ships detected above threshold."
    
    return boxed, detections, info
