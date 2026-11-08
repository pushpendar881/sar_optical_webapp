#!/usr/bin/env python3
"""
Quick script to start the backend server.
Run this in a separate terminal while the frontend is running.
"""
import os
import sys
import subprocess
from pathlib import Path

def start_backend():
    backend_dir = Path(__file__).parent / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found. Creating basic config...")
        
        # Create a basic .env file
        data_dir = backend_dir / "data"
        checkpoints_dir = data_dir / "checkpoints" 
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        env_content = f"""# Basic configuration
CHECKPOINT_PATH={checkpoints_dir.absolute()}/cyclegan_checkpoint_latest.pth
METRICS_JSON_PATH={checkpoints_dir.absolute()}/eval_metrics_comparison.json
IMG_SIZE=256
DATA_DIR={data_dir.absolute()}
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created basic .env file at {env_file}")
        print("⚠️  You'll need to copy your .pth checkpoint files to:")
        print(f"   {checkpoints_dir}")
    
    print("🚀 Starting backend server...")
    print("=" * 50)
    print("Backend will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n✅ Backend server stopped")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        print("\n💡 Try installing dependencies first:")
        print("   pip install fastapi uvicorn torch pillow numpy python-multipart")
        return False
    
    return True

if __name__ == "__main__":
    start_backend()