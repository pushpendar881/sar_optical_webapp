import torch, subprocess, sys

print("CUDA available:", torch.cuda.is_available())

try:
    import detectron2
except:
    print("Installing detectron2...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "git+https://github.com/facebookresearch/detectron2.git"
    ])
    import detectron2

print("Detectron2 ready")
import gradio as gr
import cv2
import numpy as np
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog


# Load model
cfg = get_cfg()
cfg.merge_from_file("config.yaml")
cfg.MODEL.WEIGHTS = "model_final.pth"
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.DEVICE = "cpu"   # HF Spaces free tier is CPU

MetadataCatalog.get("__unused").set(thing_classes=["ship"])
predictor = DefaultPredictor(cfg)

def detect_ships(image, confidence_threshold):
    """Run ship detection on uploaded image."""
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold

    # Convert PIL → BGR numpy
    img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    outputs = predictor(img_bgr)
    instances = outputs["instances"].to("cpu")

    # Filter by threshold
    keep = instances.scores >= confidence_threshold
    instances = instances[keep]

    metadata = MetadataCatalog.get("__unused")
    v = Visualizer(img_bgr[:, :, ::-1], metadata=metadata,
                   scale=1.0, instance_mode=ColorMode.IMAGE)
    out = v.draw_instance_predictions(instances)

    result_img = out.get_image()
    num_ships  = len(instances)
    scores     = instances.scores.tolist()
    info = f"Detected {num_ships} ship(s)\n"
    if scores:
        info += "Confidence scores: " + ", ".join([f"{s:.2f}" for s in scores])

    return result_img, info

demo = gr.Interface(
    fn=detect_ships,
    inputs=[
        gr.Image(type="pil", label="Upload SAR Image"),
        gr.Slider(0.1, 0.9, value=0.5, step=0.05, label="Confidence Threshold")
    ],
    outputs=[
        gr.Image(type="numpy", label="Detection Result"),
        gr.Textbox(label="Detection Info")
    ],
    title="🚢 HRSID Ship Detection",
    description="Upload a SAR image to detect ships using Faster R-CNN trained on HRSID dataset.",
    examples=[]
)

if __name__ == "__main__":
    demo.launch()
