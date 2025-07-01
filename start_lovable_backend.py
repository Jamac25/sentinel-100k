#!/usr/bin/env python3
"""
Sentinel 100K Lovable Backend Launcher
=====================================

Simple script to start the Lovable-compatible backend with all dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required packages"""
    packages = [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0", 
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6"
    ]
    
    print("🔧 Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    return True

def check_port():
    """Check if port 8000 is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    return result != 0

def main():
    print("🚀 Sentinel 100K - Lovable Backend Launcher")
    print("=" * 50)
    
    # Check if backend file exists
    backend_file = Path("lovable_sentinel_backend.py")
    if not backend_file.exists():
        print("❌ lovable_sentinel_backend.py not found!")
        print("Make sure you're in the correct directory.")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Check port availability
    if not check_port():
        print("⚠️  Port 8000 is already in use!")
        print("Stop any existing servers or use a different port.")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return
    
    print("\n🎯 Starting Lovable-compatible backend...")
    print("📊 API Docs: http://localhost:8000/docs")
    print("🔧 Lovable Config: http://localhost:8000/api/v1/lovable/config")
    print("💡 Frontend URL: http://localhost:8000/api/v1/")
    print("\n🔄 Press Ctrl+C to stop\n")
    
    try:
        # Start the backend using python3
        subprocess.run([sys.executable, "lovable_sentinel_backend.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend stopped gracefully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend crashed: {e}")
    except FileNotFoundError:
        print("❌ Python not found! Make sure Python is installed.")

if __name__ == "__main__":
    main() 