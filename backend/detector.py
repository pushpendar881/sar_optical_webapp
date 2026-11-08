"""HRSID Faster R-CNN ship detector (Detectron2).

Detects on the SAR image (the domain the model was trained on) and draws
boxes onto the colorized optical image, which is spatially aligned.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO_ID = os.getenv("MODEL_REPO_ID", "PUSHPENDAR/hrsid-ship-detection")
CACHE_DIR = os.getenv("HF_CACHE_DIR", str(Path(__file__).parent / "data" / "hf_cache"))

_predictor = None
_load_error: str | None = None


def load_detector(device: str = "cpu"):
    """Download weights and build a DefaultPredictor. Safe to call more than once."""
    global _predictor, _load_error
    if _predictor is not None:
        return _predictor
    if _load_error:
        raise RuntimeError(_load_error)

    try:
        from detectron2.config import get_cfg
        from detectron2.data import MetadataCatalog
        from detectron2.engine import DefaultPredictor
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        _load_error = (
            "Ship detector extras are missing. Install with: "
            "pip install opencv-python-headless huggingface_hub "
            "'git+https://github.com/facebookresearch/detectron2.git'"
        )
        raise RuntimeError(_load_error) from exc

    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
    token = os.getenv("HF_TOKEN")
    print(f"Downloading HRSID detector from {REPO_ID}...")
    model_path = hf_hub_download(
        repo_id=REPO_ID,
        filename="model_final.pth",
        cache_dir=CACHE_DIR,
        token=token,
    )
    config_path = hf_hub_download(
        repo_id=REPO_ID,
        filename="config.yaml",
        cache_dir=CACHE_DIR,
        token=token,
    )

    cfg = get_cfg()
    cfg.merge_from_file(config_path)
    cfg.MODEL.WEIGHTS = model_path
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.05
    cfg.MODEL.DEVICE = "cuda" if device == "cuda" else "cpu"
    MetadataCatalog.get("__unused").set(thing_classes=["ship"])
    _predictor = DefaultPredictor(cfg)
    print(f"HRSID detector loaded on {cfg.MODEL.DEVICE}")
    return _predictor


def detector_available() -> bool:
    return _predictor is not None


def detector_error() -> str | None:
    return _load_error


def _to_bgr(image: Image.Image, size: tuple[int, int]) -> np.ndarray:
    rgb = np.array(image.convert("RGB").resize(size, Image.Resampling.LANCZOS), dtype=np.uint8)
    return rgb[:, :, ::-1].copy()


def _font():
    try:
        return ImageFont.truetype("Helvetica.ttc", 12)
    except OSError:
        return ImageFont.load_default()


def detect_and_overlay(
    sar_image: Image.Image,
    colorized_rgb: np.ndarray,
    confidence_threshold: float = 0.5,
) -> tuple[Image.Image, list[dict], str]:
    """Run detection on SAR and overlay boxes on the colorized RGB array."""
    if _predictor is None:
        raise RuntimeError(_load_error or "Detector is not loaded.")

    h, w = colorized_rgb.shape[:2]
    img_bgr = _to_bgr(sar_image, (w, h))
    outputs = _predictor(img_bgr)
    instances = outputs["instances"].to("cpu")
    keep = instances.scores >= float(confidence_threshold)
    instances = instances[keep]

    detections: list[dict] = []
    scores = instances.scores.tolist() if len(instances) else []
    if scores and hasattr(instances, "pred_boxes"):
        boxes = instances.pred_boxes.tensor.tolist()
        for i, (box, score) in enumerate(zip(boxes, scores)):
            x1, y1, x2, y2 = [int(c) for c in box]
            detections.append(
                {"id": i + 1, "bbox": [x1, y1, x2, y2], "score": round(float(score), 4)}
            )

    boxed = Image.fromarray(colorized_rgb.copy())
    draw = ImageDraw.Draw(boxed)
    font = _font()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        draw.rectangle([x1, y1, x2, y2], outline=(37, 99, 235), width=2)
        label = f"ship {det['score']:.2f}"
        ty = max(0, y1 - 14)
        draw.rectangle([x1, ty, x1 + 78, ty + 14], fill=(37, 99, 235))
        draw.text((x1 + 4, ty + 1), label, fill=(255, 255, 255), font=font)

    num = len(detections)
    info = f"Detected {num} ship(s)"
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
