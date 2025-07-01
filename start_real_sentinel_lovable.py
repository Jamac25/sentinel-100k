#!/usr/bin/env python3
"""
Sentinel 100K Real Backend Launcher for Lovable
==============================================

Starts both the real Sentinel backend and the Lovable-compatible interface.
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_port(port):
    """Check if port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def install_dependencies():
    """Install required packages"""
    packages = [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0", 
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6",
        "httpx>=0.24.0",
        "sqlalchemy>=1.4.0"
    ]
    
    print("🔧 Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    return True

def start_sentinel_backend():
    """Start the real Sentinel backend"""
    print("🚀 Starting Sentinel 100K backend...")
    
    # Change to personal_finance_agent directory
    backend_dir = Path("personal_finance_agent")
    if not backend_dir.exists():
        print("❌ personal_finance_agent directory not found!")
        return None
    
    os.chdir(backend_dir)
    
    try:
        # Start the backend
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        print("✅ Sentinel backend starting on port 8000...")
        time.sleep(5)  # Give it time to start
        
        # Check if it's running
        if process.poll() is None:
            print("✅ Sentinel backend is running!")
            return process
        else:
            print("❌ Sentinel backend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start Sentinel backend: {e}")
        return None
    finally:
        os.chdir("..")  # Return to main directory

def start_lovable_interface():
    """Start the Lovable interface"""
    print("🎨 Starting Lovable interface...")
    
    try:
        process = subprocess.Popen([
            sys.executable, "lovable_sentinel_real_backend.py"
        ])
        
        print("✅ Lovable interface starting on port 9000...")
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Lovable interface is running!")
            return process
        else:
            print("❌ Lovable interface failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start Lovable interface: {e}")
        return None

def main():
    processes = []
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down services...")
        for process in processes:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print("👋 All services stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Sentinel 100K Real Backend + Lovable Launcher")
    print("=" * 60)
    
    # Check files exist
    if not Path("lovable_sentinel_real_backend.py").exists():
        print("❌ lovable_sentinel_real_backend.py not found!")
        return
    
    if not Path("personal_finance_agent").exists():
        print("❌ personal_finance_agent directory not found!")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Check ports
    if not check_port(8000):
        print("⚠️  Port 8000 is already in use!")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return
    
    if not check_port(9000):
        print("⚠️  Port 9000 is already in use!")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return
    
    print("\n🎯 Starting services...")
    
    # Start Sentinel backend first
    backend_process = start_sentinel_backend()
    if backend_process:
        processes.append(backend_process)
    else:
        print("❌ Cannot start Lovable interface without backend")
        return
    
    # Start Lovable interface
    lovable_process = start_lovable_interface()
    if lovable_process:
        processes.append(lovable_process)
    
    if not processes:
        print("❌ No services started successfully")
        return
    
    print("\n🎉 All services started successfully!")
    print("=" * 60)
    print("📊 Sentinel Backend: http://localhost:8000")
    print("📚 Backend Docs: http://localhost:8000/docs")
    print("🎨 Lovable API: http://localhost:9000") 
    print("📋 Lovable Docs: http://localhost:9000/docs")
    print("🔧 Lovable Config: http://localhost:9000/api/v1/lovable/config")
    print("💡 Frontend URL: http://localhost:9000/api/v1/")
    print("\n💾 Data Source: Real Sentinel Database")
    print("🔌 WebSocket: ws://localhost:9000/ws")
    print("\n🔄 Press Ctrl+C to stop all services")
    
    # Keep running
    try:
        while True:
            # Check if processes are still running
            running_count = sum(1 for p in processes if p.poll() is None)
            if running_count == 0:
                print("❌ All services stopped unexpectedly")
                break
            time.sleep(5)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 