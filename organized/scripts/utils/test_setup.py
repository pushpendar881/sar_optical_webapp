#!/usr/bin/env python3
"""
Test script to verify the SAR-to-Optical web app setup.
Run this after setup to ensure everything is working correctly.
"""
import requests
import json
import time
from pathlib import Path

def test_backend_health():
    """Test if backend server is running and responding"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/api/model-info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running")
            print(f"   Device: {data.get('device', 'unknown')}")
            print(f"   Checkpoint: {data.get('checkpoint', 'unknown')}")
            print(f"   Architecture: {data.get('architecture', 'unknown')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend_health():
    """Test if frontend server is running"""
    print("\n🔍 Testing frontend health...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running on http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server not running on http://localhost:3000")
        return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    endpoints = [
        ("/api/model-info", "Model Info"),
        ("/api/history", "History"),
        ("/api/metrics", "Metrics"),
    ]
    
    all_passed = True
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} endpoint working")
            else:
                print(f"❌ {name} endpoint failed (status {response.status_code})")
                all_passed = False
        except Exception as e:
            print(f"❌ {name} endpoint error: {e}")
            all_passed = False
    
    return all_passed

def test_file_structure():
    """Test if required files and directories exist"""
    print("\n🔍 Testing file structure...")
    
    required_paths = [
        ("backend/app.py", "Backend main file"),
        ("backend/model.py", "Model definition"),
        ("backend/requirements.txt", "Backend requirements"),
        ("backend/.env", "Environment config"),
        ("backend/data", "Data directory"),
        ("backend/data/checkpoints", "Checkpoints directory"),
        ("frontend/package.json", "Frontend package config"),
        ("frontend/app/page.tsx", "Frontend main page"),
    ]
    
    all_exist = True
    for path, description in required_paths:
        if Path(path).exists():
            print(f"✅ {description}")
        else:
            print(f"❌ Missing: {description} ({path})")
            all_exist = False
    
    return all_exist

def check_checkpoint_files():
    """Check if checkpoint files exist"""
    print("\n🔍 Checking checkpoint files...")
    
    checkpoint_dir = Path("backend/data/checkpoints")
    if not checkpoint_dir.exists():
        print("❌ Checkpoints directory not found")
        return False
    
    checkpoint_files = list(checkpoint_dir.glob("*.pth"))
    if checkpoint_files:
        print(f"✅ Found {len(checkpoint_files)} checkpoint file(s):")
        for ckpt in checkpoint_files:
            size_mb = ckpt.stat().st_size / (1024 * 1024)
            print(f"   📄 {ckpt.name} ({size_mb:.1f} MB)")
        
        # Check for metrics file
        metrics_file = checkpoint_dir / "eval_metrics_comparison.json"
        if metrics_file.exists():
            print("✅ Evaluation metrics file found")
        else:
            print("ℹ️  No evaluation metrics file (optional)")
        
        return True
    else:
        print("❌ No checkpoint files found in backend/data/checkpoints/")
        return False

def main():
    print("SAR-to-Optical Web App - Setup Verification")
    print("=" * 50)
    
    # Test file structure first
    structure_ok = test_file_structure()
    checkpoint_ok = check_checkpoint_files()
    
    if not (structure_ok and checkpoint_ok):
        print("\n❌ Setup incomplete - fix file structure issues first")
        return False
    
    # Test servers
    backend_ok = test_backend_health()
    frontend_ok = test_frontend_health()
    
    if backend_ok:
        api_ok = test_api_endpoints()
    else:
        api_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if structure_ok and checkpoint_ok and backend_ok and frontend_ok and api_ok:
        print("🎉 ALL TESTS PASSED!")
        print("\n🌐 Your SAR-to-Optical web app is ready!")
        print("   Frontend: http://localhost:3000")
        print("   Backend:  http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("\n📝 Issues to fix:")
        if not structure_ok: print("   - Missing required files")
        if not checkpoint_ok: print("   - Checkpoint files not found")
        if not backend_ok: print("   - Backend server not running")
        if not frontend_ok: print("   - Frontend server not running")
        if not api_ok: print("   - API endpoints not working")
        
        print("\n💡 Try running the setup script again:")
        print("   python setup.py /path/to/your/seg_cyclegan_project")
        return False

if __name__ == "__main__":
    main()