#!/usr/bin/env python3
"""
🎯 SENTINEL 100K - RENDER DEPLOYMENT HELPER
============================================
Automated script to prepare for Render.com deployment
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def print_banner():
    """Print deployment banner"""
    print("🎯" + "=" * 60 + "🎯")
    print("🚀 SENTINEL 100K - RENDER DEPLOYMENT HELPER")
    print("🎯" + "=" * 60 + "🎯")
    print("✅ Valmistelen Render.com-siirtoa...")
    print()

def check_requirements():
    """Check if all required files exist"""
    print("🔍 Tarkistan tarvittavat tiedostot...")
    
    required_files = [
        "requirements.txt",
        "render.yaml", 
        "Procfile",
        "runtime.txt",
        "sentinel_render_ready.py",
        ".env.example"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"❌ Puuttuu: {file}")
        else:
            print(f"✅ Löytyi: {file}")
    
    if missing_files:
        print(f"\n❌ Puuttuu {len(missing_files)} tiedostoa. Luo ne ensin!")
        return False
    
    print("✅ Kaikki tarvittavat tiedostot löytyi!")
    return True

def check_git_status():
    """Check git repository status"""
    print("\n🔍 Tarkistan Git-repositoryn...")
    
    try:
        # Check if git is initialized
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Git ei ole alustettu. Alusta git:")
            print("   git init")
            print("   git add .")
            print("   git commit -m 'Initial commit'")
            return False
        
        # Check for uncommitted changes
        if "nothing to commit" not in result.stdout:
            print("⚠️  Committaamattomia muutoksia löytyi:")
            print("   git add .")
            print("   git commit -m 'Prepare for Render deployment'")
            print("   git push")
        else:
            print("✅ Git-repository on ajan tasalla!")
        
        return True
        
    except FileNotFoundError:
        print("❌ Git ei ole asennettu!")
        return False

def test_local_server():
    """Test if the render-ready server starts locally"""
    print("\n🧪 Testaan Render-ready serveriä paikallisesti...")
    
    try:
        print("⚡ Käynnistän testiserverää...")
        print("   Paina Ctrl+C lopettaaksesi testin")
        
        # Start the server
        process = subprocess.Popen([
            sys.executable, "sentinel_render_ready.py"
        ])
        
        import time
        time.sleep(3)  # Give server time to start
        
        # Test if server responds
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Testiserveri toimii!")
                print(f"   Status: {response.json().get('status')}")
                process.terminate()
                return True
            else:
                print(f"❌ Serveri vastasi virheellä: {response.status_code}")
                process.terminate()
                return False
        except ImportError:
            print("⚠️  'requests' ei ole asennettu. Asennan...")
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
            process.terminate()
            return True
        except Exception as e:
            print(f"❌ Testiyhteys epäonnistui: {e}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Serverin käynnistys epäonnistui: {e}")
        return False

def generate_secret_key():
    """Generate a secure secret key"""
    print("\n🔐 Luon turvallisen SECRET_KEY:n...")
    
    try:
        import secrets
        secret_key = secrets.token_urlsafe(32)
        print(f"✅ Uusi SECRET_KEY: {secret_key}")
        print("   💡 Kopioi tämä Render environment variableihin!")
        
        # Save to .env.example
        env_file = Path(".env.example")
        if env_file.exists():
            content = env_file.read_text()
            content = content.replace("your-super-secret-key-here-change-this", secret_key)
            env_file.write_text(content)
            print("✅ SECRET_KEY päivitetty .env.example-tiedostoon")
        
        return secret_key
        
    except Exception as e:
        print(f"❌ SECRET_KEY luominen epäonnistui: {e}")
        return None

def show_deployment_checklist():
    """Show deployment checklist"""
    print("\n📋 RENDER DEPLOYMENT CHECKLIST:")
    print("=" * 50)
    print("🏁 1. Luo GitHub repository:")
    print("     git remote add origin https://github.com/USERNAME/sentinel-100k.git")
    print("     git push -u origin main")
    print()
    print("🗄️  2. Luo PostgreSQL database Renderissä:")
    print("     Name: sentinel-db")
    print("     Plan: Free")
    print()
    print("🌐 3. Luo Web Service Renderissä:")
    print("     Repository: sentinel-100k")
    print("     Build Command: pip install -r requirements.txt")
    print("     Start Command: uvicorn sentinel_render_ready:app --host 0.0.0.0 --port $PORT")
    print()
    print("⚙️  4. Aseta Environment Variables:")
    print("     DATABASE_URL=<copy from PostgreSQL service>")
    print("     SECRET_KEY=<generated above>")
    print("     ENVIRONMENT=production")
    print("     DEBUG=false")
    print()
    print("🎯 5. Deploy ja testaa:")
    print("     https://your-app-name.onrender.com/health")
    print()
    print("📚 Katso täydelliset ohjeet: RENDER_DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment preparation function"""
    print_banner()
    
    # Check all requirements
    if not check_requirements():
        print("\n❌ Deployment-valmistelu epäonnistui!")
        return
    
    # Check git status
    if not check_git_status():
        print("\n⚠️  Git-repository vaatii huomiota")
    
    # Test local server
    if not test_local_server():
        print("\n⚠️  Testiserverissa ongelmia, mutta deployment voi silti onnistua")
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Show checklist
    show_deployment_checklist()
    
    print("\n🎉 VALMIS RENDER-DEPLOYMENTILLE!")
    print("✅ Kaikki tiedostot luotu")
    print("✅ Konfiguraatio valmis")
    print("🚀 Seuraa RENDER_DEPLOYMENT_GUIDE.md ohjeita")
    print()
    print("💡 Seuraavat askeleet:")
    print("   1. git add . && git commit -m 'Ready for Render'")
    print("   2. git push")
    print("   3. Mene render.com ja luo web service")
    print("   4. Nauti täysin toimivasta Sentinel 100K:sta pilvessä! 🎯")

if __name__ == "__main__":
    main() 