#!/usr/bin/env python3
"""
One-click deployment script for SAR-to-Optical web app.

This script will:
1. Set up your project files
2. Install all dependencies
3. Start both servers
4. Open the web app in your browser

Usage:
    python deploy.py /path/to/your/seg_cyclegan_project
"""
import argparse
import os
import subprocess
import sys
import webbrowser
import time
from pathlib import Path
from setup import copy_project_files, create_env_file, install_dependencies

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    # Check Python dependencies
    try:
        import torch
        import PIL
        import fastapi
    except ImportError as e:
        missing.append(f"Python packages: {e}")
    
    # Check Node.js
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("Node.js not found")
    
    # Check npm
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("npm not found")
    
    return missing

def start_backend(webapp_root: Path):
    """Start the FastAPI backend server"""
    backend_dir = webapp_root / "backend"
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ], cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_frontend(webapp_root: Path):
    """Start the Next.js frontend server"""
    frontend_dir = webapp_root / "frontend"
    return subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def wait_for_server(url, timeout=30):
    """Wait for server to become available"""
    import urllib.request
    import urllib.error
    
    for _ in range(timeout):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, ConnectionResetError):
            time.sleep(1)
    return False

def main():
    parser = argparse.ArgumentParser(description="Deploy SAR-to-Optical web app")
    parser.add_argument("project_path", help="Path to your seg_cyclegan_project directory")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies")
    args = parser.parse_args()
    
    # Check dependencies first
    print("🔍 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print("❌ Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        
        if args.check_only:
            return
            
        print("\n📦 Installing missing dependencies...")
        if "Python packages" in str(missing):
            print("Installing Python packages...")
            subprocess.run([sys.executable, "-m", "pip", "install", 
                           "torch", "torchvision", "fastapi", "uvicorn[standard]", 
                           "python-multipart", "pillow", "numpy"], check=True)
        
        if "Node.js" in str(missing) or "npm" in str(missing):
            print("⚠️  Please install Node.js and npm manually from: https://nodejs.org/")
            print("   Then run this script again.")
            return
    else:
        print("✅ All dependencies are available!")
    
    if args.check_only:
        return
    
    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"❌ Project path {project_path} does not exist")
        sys.exit(1)
    
    webapp_root = Path(__file__).parent
    
    try:
        print(f"\n🚀 Deploying SAR-to-Optical web app...")
        print("=" * 50)
        
        # Setup project files
        print("1️⃣  Setting up project files...")
        checkpoints_dir = copy_project_files(project_path, webapp_root)
        create_env_file(webapp_root, checkpoints_dir)
        
        # Install dependencies
        print("\n2️⃣  Installing dependencies...")
        install_dependencies(webapp_root)
        
        # Start servers
        print("\n3️⃣  Starting servers...")
        backend_process = start_backend(webapp_root)
        time.sleep(3)  # Give backend time to start
        
        frontend_process = start_frontend(webapp_root)
        time.sleep(5)  # Give frontend time to start
        
        # Wait for servers to be ready
        print("⏳ Waiting for servers to be ready...")
        
        backend_ready = wait_for_server("http://localhost:8000/api/model-info", timeout=30)
        frontend_ready = wait_for_server("http://localhost:3000", timeout=30)
        
        if not backend_ready:
            print("⚠️  Backend might not be ready yet, but continuing...")
        
        if not frontend_ready:
            print("⚠️  Frontend might not be ready yet, but continuing...")
        
        print("\n🎉 Deployment successful!")
        print("=" * 50)
        print("🌐 Frontend:     http://localhost:3000")
        print("🔧 Backend API:  http://localhost:8000")
        print("📚 API docs:     http://localhost:8000/docs")
        print("=" * 50)
        
        # Open browser
        if not args.no_browser:
            print("🌍 Opening web app in your browser...")
            webbrowser.open("http://localhost:3000")
        
        print("\n✨ Your SAR-to-Optical web app is now running!")
        print("   Upload a SAR image to see the magic happen!")
        print("\n⏹️  Press Ctrl+C to stop the servers")
        
        # Keep running until interrupted
        try:
            while True:
                if backend_process.poll() is not None:
                    print("⚠️  Backend process stopped")
                    break
                if frontend_process.poll() is not None:
                    print("⚠️  Frontend process stopped")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            
        # Cleanup
        backend_process.terminate()
        frontend_process.terminate()
        
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ Servers stopped cleanly")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()