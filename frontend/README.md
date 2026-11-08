# SAR -> Optical Colorization -- Demo Web App

FastAPI backend + single-page frontend, wraps the trained Seg-CycleGAN checkpoint.

## Structure
```
backend/
  app.py            FastAPI app (predict / history / metrics endpoints)
  model.py          Generator architecture (same as training notebook)
  requirements.txt
frontend/
  index.html        Single-page UI, served by the backend at "/"
```

## Run (on the GPU instance where checkpoints/dataset already live)

```bash
cd backend
pip install -r requirements.txt --break-system-packages

# only needed if your checkpoint isn't at the default path
export CHECKPOINT_PATH=/home/seg_cyclegan_project/checkpoints/cyclegan_checkpoint_latest.pth
# optional: point at the comparison JSON from the eval notebook, if you generated one
export METRICS_JSON_PATH=/home/seg_cyclegan_project/checkpoints/eval_metrics_comparison.json

uvicorn app:app --host 0.0.0.0 --port 8000
```

Open `http://<instance-ip>:8000` (or `http://localhost:8000` if running locally / via SSH port-forward).

Every prediction is saved to `backend/data/` (`uploads/`, `outputs/`) and logged in `backend/data/history.db`
(SQLite -- no separate DB server to set up).

## Notes
- If the GPU instance only exposes SSH, forward the port instead of opening it publicly:
  `ssh -L 8000:localhost:8000 user@instance`, then open `http://localhost:8000` on your own machine.
- The metrics panel reads whatever JSON the eval notebook wrote (`eval_metrics_comparison.json`) --
  regenerate that first if you want the panel populated for the demo.
