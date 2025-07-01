#!/usr/bin/env python3
"""
🎯 SENTINEL 100K - 100% STARTUP LAUNCHER
======================================
Käynnistää täydellisen Sentinel järjestelmän yhdellä komennolla!
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("🎯" + "="*60 + "🎯")
    print("🚀 SENTINEL 100K - 100% COMPLETE SYSTEM STARTUP")
    print("🎯" + "="*60 + "🎯")
    print()
    print("✅ SYVÄ ONBOARDING - Deep user profiling with CV analysis")
    print("✅ 7-VIIKON SYKLIT - Progressive weekly challenges 300€→600€")
    print("✅ YÖANALYYSI - Automated night analysis at 2:00 AM daily")
    print("✅ AI VALMENNUS - Complete AI coaching system")
    print("✅ KAIKKI PALVELUT - All previous features integrated")
    print()
    print("🎯 STATUS: 100% COMPLETE - EI PUUTTEITA!")
    print("🎯" + "="*60 + "🎯")
    print()

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic", 
        "schedule"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - PUUTTUU")
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "cv_uploads",
        "data_backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def start_backend():
    """Start the complete backend"""
    print("🚀 Starting Sentinel 100K Complete Backend...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 WebSocket: ws://localhost:8000/ws")
    print()
    print("🌙 Night Analysis: Automated at 2:00 AM daily")
    print("📊 Real-time Dashboard: All systems monitored")
    print()
    print("💡 USAGE EXAMPLES:")
    print("   Start Onboarding: POST /api/v1/onboarding/start")
    print("   Upload CV: POST /api/v1/upload/cv")
    print("   Get Weekly Cycle: GET /api/v1/cycles/current/{user_id}")
    print("   Night Analysis: GET /api/v1/analysis/night/latest")
    print()
    print("🎯 Press Ctrl+C to stop the server")
    print("🎯" + "="*60 + "🎯")
    
    try:
        # Run the complete backend
        subprocess.run([sys.executable, "sentinel_100_percent_complete.py"])
    except KeyboardInterrupt:
        print("\n🛑 Sentinel 100K Complete Backend stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def main():
    """Main startup function"""
    print_banner()
    
    # Check if backend file exists
    if not Path("sentinel_100_percent_complete.py").exists():
        print("❌ Backend file not found: sentinel_100_percent_complete.py")
        print("Please ensure the file is in the same directory")
        return
    
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed. Please install required packages.")
        return
    
    print("\n📁 Creating directories...")
    create_directories()
    
    print("\n🎯 All systems ready! Starting 100% Complete Backend...")
    time.sleep(2)
    
    start_backend()

if __name__ == "__main__":
    main() 