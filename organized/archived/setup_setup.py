#!/usr/bin/env python3
"""
Setup script to integrate a SAR-to-Optical project folder with the web app.

Usage:
    python setup.py /path/to/your/seg_cyclegan_project

This will:
1. Copy the checkpoint files to the backend
2. Copy evaluation metrics if available 
3. Update environment variables
4. Start both backend and frontend servers
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
import json

def copy_project_files(project_path: Path, webapp_root: Path):
    """Copy necessary files from the project to the webapp structure"""
    print(f"Setting up project from: {project_path}")
    
    # Create data directory structure
    data_dir = webapp_root / "backend" / "data"
    checkpoints_dir = data_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy checkpoint files
    project_checkpoints = project_path / "checkpoints"
    if project_checkpoints.exists():
        print("Copying checkpoint files...")
        for ckpt_file in project_checkpoints.glob("*.pth"):
            shutil.copy2(ckpt_file, checkpoints_dir)
            print(f"  Copied {ckpt_file.name}")
        
        # Copy evaluation metrics if available
        metrics_file = project_checkpoints / "eval_metrics_comparison.json"
        if metrics_file.exists():
            shutil.copy2(metrics_file, checkpoints_dir)
            print(f"  Copied {metrics_file.name}")
    else:
        print(f"Warning: No checkpoints directory found in {project_path}")
    
    # Look for common checkpoint patterns in the project root
    checkpoint_patterns = ["*.pth", "*cyclegan*.pth", "*G_AB*.pth", "*latest*.pth"]
    found_checkpoints = []
    
    for pattern in checkpoint_patterns:
        for model_file in project_path.glob(pattern):
            if not (checkpoints_dir / model_file.name).exists():
                shutil.copy2(model_file, checkpoints_dir)
                print(f"  Copied {model_file.name}")
                found_checkpoints.append(model_file.name)
    
    # Look for evaluation metrics in project root as well
    for metrics_pattern in ["*metrics*.json", "*comparison*.json", "*eval*.json"]:
        for metrics_file in project_path.glob(metrics_pattern):
            if "comparison" in metrics_file.name.lower() or "eval" in metrics_file.name.lower():
                dest_file = checkpoints_dir / "eval_metrics_comparison.json"
                shutil.copy2(metrics_file, dest_file)
                print(f"  Copied {metrics_file.name} as eval_metrics_comparison.json")
    
    # Also check common subdirectories
    for subdir in ["outputs", "results", "eval_tmp"]:
        subdir_path = project_path / subdir
        if subdir_path.exists():
            for metrics_file in subdir_path.rglob("*metrics*.json"):
                if "comparison" in metrics_file.name.lower():
                    dest_file = checkpoints_dir / "eval_metrics_comparison.json"
                    shutil.copy2(metrics_file, dest_file)
                    print(f"  Found and copied {metrics_file} as eval_metrics_comparison.json")
                    break
    
    if not found_checkpoints and not any(checkpoints_dir.glob("*.pth")):
        print("⚠️  Warning: No .pth checkpoint files found!")
        print("   Please manually copy your model checkpoint to backend/data/checkpoints/")
    
    return checkpoints_dir

def create_env_file(webapp_root: Path, checkpoints_dir: Path):
    """Create environment configuration file"""
    env_file = webapp_root / "backend" / ".env"
    
    # Find the latest checkpoint
    checkpoint_files = list(checkpoints_dir.glob("*.pth"))
    if not checkpoint_files:
        raise RuntimeError("No checkpoint files found after copying!")
    
    # Prefer cyclegan_checkpoint_latest.pth, otherwise take the first one
    checkpoint_path = None
    for ckpt in checkpoint_files:
        if "latest" in ckpt.name.lower():
            checkpoint_path = ckpt
            break
    if not checkpoint_path:
        checkpoint_path = checkpoint_files[0]
    
    metrics_path = checkpoints_dir / "eval_metrics_comparison.json"
    
    env_content = f"""# Auto-generated environment configuration
CHECKPOINT_PATH={checkpoint_path.absolute()}
METRICS_JSON_PATH={metrics_path.absolute() if metrics_path.exists() else ""}
IMG_SIZE=256
DATA_DIR={webapp_root.absolute()}/backend/data
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"Created environment file: {env_file}")
    print(f"Using checkpoint: {checkpoint_path.name}")
    
    return env_file

def install_dependencies(webapp_root: Path):
    """Install Python dependencies for backend"""
    backend_dir = webapp_root / "backend"
    requirements_file = backend_dir / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing Python dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, cwd=backend_dir)
        print("✓ Backend dependencies installed")
    
    # Install frontend dependencies if needed
    frontend_dir = webapp_root / "frontend"
    package_json = frontend_dir / "package.json"
    
    if package_json.exists() and not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], check=True, cwd=frontend_dir)
        print("✓ Frontend dependencies installed")

def start_servers(webapp_root: Path):
    """Start both backend and frontend servers"""
    backend_dir = webapp_root / "backend"
    frontend_dir = webapp_root / "frontend"
    
    print("\nStarting servers...")
    print("=" * 50)
    
    # Start backend
    print("Starting backend server on http://localhost:8000")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ], cwd=backend_dir)
    
    # Give backend time to start
    import time
    time.sleep(3)
    
    # Start frontend
    print("Starting frontend server on http://localhost:3000")
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=frontend_dir)
    
    print("\n🚀 Both servers are starting up!")
    print("🔗 Frontend: http://localhost:3000")
    print("🔗 Backend API: http://localhost:8000")
    print("📊 API docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✓ Servers stopped")

def main():
    parser = argparse.ArgumentParser(description="Setup SAR-to-Optical web app with your project")
    parser.add_argument("project_path", help="Path to your seg_cyclegan_project directory")
    parser.add_argument("--no-start", action="store_true", help="Don't start servers after setup")
    args = parser.parse_args()
    
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"Error: Project path {project_path} does not exist")
        sys.exit(1)
    
    webapp_root = Path(__file__).parent
    
    try:
        # Copy project files
        checkpoints_dir = copy_project_files(project_path, webapp_root)
        
        # Create environment configuration
        create_env_file(webapp_root, checkpoints_dir)
        
        # Install dependencies
        install_dependencies(webapp_root)
        
        print("\n✅ Setup completed successfully!")
        
        if not args.no_start:
            start_servers(webapp_root)
        else:
            print("\nTo start the servers later, run:")
            print("  cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
            print("  cd frontend && npm run dev")
    
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()