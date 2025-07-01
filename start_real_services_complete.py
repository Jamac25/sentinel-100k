#!/usr/bin/env python3
"""
🎯 SENTINEL 100K - REAL SERVICES STARTUP LAUNCHER
================================================
Käynnistää OIKEAT palvelut (ei mock!)

✅ IdeaEngine™ (627 lines)
✅ SchedulerService (475 lines) 
✅ SentinelWatchdog™ (540 lines)
✅ SentinelLearning™ (632 lines)
✅ Emergency Protocol
✅ ML Training & Automation
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_real_banner():
    print("🎯" + "="*70 + "🎯")
    print("🚀 SENTINEL 100K - REAL SERVICES COMPLETE STARTUP")
    print("🎯" + "="*70 + "🎯")
    print()
    print("✅ OIKEAT PALVELUT (EI MOCK!) - REAL SERVICES INTEGRATION")
    print("✅ IdeaEngine™ - 627 riviä aitoa koodia")
    print("✅ SchedulerService - 475 riviä automaatiota") 
    print("✅ SentinelWatchdog™ - 540 riviä hätätila-protokollaa")
    print("✅ SentinelLearning™ - 632 riviä ML-oppimista")
    print("✅ YHTEENSÄ: 2,274 riviä AITOJA PALVELUITA!")
    print()
    print("🔥 STATUS: KAIKKI SEURAAVAT ASKELEET TOTEUTETTU!")
    print("🔥 ❌ MOCK SERVICES - KÄYTÖSSÄ OIKEAT ALGORITMIT")
    print("🎯" + "="*70 + "🎯")
    print()

def check_real_services():
    """Check if real services directory exists"""
    services_path = Path("personal_finance_agent/app/services")
    
    if not services_path.exists():
        print("❌ VIRHE: personal_finance_agent/app/services kansio puuttuu!")
        print("   Varmista että olet oikeassa hakemistossa")
        return False
    
    required_services = [
        "idea_engine.py",
        "scheduler_service.py", 
        "sentinel_watchdog_service.py",
        "sentinel_learning_engine.py",
        "income_stream_intelligence.py",
        "liabilities_insight.py"
    ]
    
    missing_services = []
    for service in required_services:
        if not (services_path / service).exists():
            missing_services.append(service)
    
    if missing_services:
        print(f"❌ PUUTTUVAT PALVELUT: {', '.join(missing_services)}")
        return False
    
    print("✅ KAIKKI OIKEAT PALVELUT LÖYTYI!")
    for service in required_services:
        file_size = (services_path / service).stat().st_size
        print(f"   📄 {service} ({file_size//1024}KB)")
    
    return True

def check_dependencies():
    """Check required packages"""
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

def start_real_backend():
    """Start the REAL services backend"""
    print("🚀 Starting Sentinel 100K REAL SERVICES Backend...")
    print("📡 Server will be available at: http://localhost:8100")
    print("📚 API Documentation: http://localhost:8100/docs")
    print()
    print("🔥 REAL SERVICES ACTIVE:")
    print("   💡 IdeaEngine™: /api/v1/intelligence/ideas/real-daily/{user_id}")
    print("   🚨 Watchdog™: /api/v1/watchdog/real-status/{user_id}")
    print("   🌙 Night Analysis: /api/v1/analysis/real-night/latest")
    print("   ⚫ Emergency: /api/v1/watchdog/activate-emergency/{user_id}")
    print()
    print("🌙 REAL Night Analysis: Automated at 2:00 AM with actual services")
    print("🚨 REAL Emergency Protocol: Watchdog hätätila-toiminnot")
    print("💡 REAL Daily Ideas: Personoidut ansaintaideat")
    print()
    print("🎯 Press Ctrl+C to stop the server")
    print("🎯" + "="*70 + "🎯")
    
    try:
        subprocess.run([sys.executable, "sentinel_real_services_complete.py"])
    except KeyboardInterrupt:
        print("\n🛑 Sentinel REAL Services Backend stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def main():
    print_real_banner()
    
    # Check if backend file exists
    if not Path("sentinel_real_services_complete.py").exists():
        print("❌ Backend file not found: sentinel_real_services_complete.py")
        print("Please ensure the file is in the same directory")
        return
    
    print("🔍 Checking REAL services...")
    if not check_real_services():
        print("❌ Real services check failed.")
        return
    
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed.")
        return
    
    print("\n🎯 All systems ready! Starting REAL SERVICES Backend...")
    time.sleep(2)
    
    start_real_backend()

if __name__ == "__main__":
    main() 