#!/usr/bin/env python3
"""
🚀 SENTINEL 100K - STREAMLIT LAUNCHER
=====================================
Käynnistää yksinkertaisen Streamlit-sovelluksen joka yhdistyy Render-backendiin
"""

import subprocess
import sys
import os

def install_requirements():
    """Asenna tarvittavat riippuvuudet"""
    print("📦 Asennetaan riippuvuuksia...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "simple_requirements.txt"])
        print("✅ Riippuvuudet asennettu!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Virhe riippuvuuksien asennuksessa: {e}")
        return False

def start_streamlit():
    """Käynnistä Streamlit-sovellus"""
    print("🚀 Käynnistetään Streamlit...")
    
    # Streamlit-komento
    cmd = [
        sys.executable, "-m", "streamlit", "run", "simple_streamlit.py",
        "--server.port", "8503",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ]
    
    print(f"💻 Komento: {' '.join(cmd)}")
    print("\n" + "="*60)
    print("🌐 STREAMLIT KÄYNNISTYY...")
    print("="*60)
    print("📱 URL: http://localhost:8503")
    print("🔗 Backend: https://sentinel-100k.onrender.com")
    print("🇫🇮 Kieli: Suomi")
    print("="*60)
    print("🛑 Pysäytä painamalla Ctrl+C")
    print("="*60 + "\n")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Virhe Streamlitin käynnistyksessä: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Streamlit pysäytetty käyttäjän toimesta")
        return True
    
    return True

def main():
    """Pääfunktio"""
    print("🎯 SENTINEL 100K - STREAMLIT LAUNCHER")
    print("=" * 50)
    
    # Tarkista että tiedostot ovat olemassa
    if not os.path.exists("simple_streamlit.py"):
        print("❌ simple_streamlit.py ei löydy!")
        return
    
    if not os.path.exists("simple_requirements.txt"):
        print("❌ simple_requirements.txt ei löydy!")
        return
    
    # Asenna riippuvuudet
    if not install_requirements():
        return
    
    # Käynnistä Streamlit
    start_streamlit()

if __name__ == "__main__":
    main() 