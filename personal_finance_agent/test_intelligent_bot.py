#!/usr/bin/env python3
"""
🧪 Testi älykkäälle Telegram-botille
"""

import os
import requests
import json
from datetime import datetime

def test_bot_connection():
    """Testaa Telegram-botin yhteys"""
    token = os.getenv('TELEGRAM_BOT_TOKEN', '7991879935:AAFYVHdzF0nIQ1IHjUBxQ1cLuopzlGC4vWI')
    
    print("🧪 TESTAA TELEGRAM-BOTTI")
    print("=" * 40)
    print(f"🔑 Token: {token[:10]}...")
    
    try:
        # Testaa bot info
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print("✅ Telegram-botti yhteys OK!")
                print(f"📛 Nimi: {bot_info['first_name']}")
                print(f"👤 Username: @{bot_info['username']}")
                print(f"🆔 ID: {bot_info['id']}")
                return True
            else:
                print("❌ Bot API virhe:", data.get('description', 'Tuntematon virhe'))
                return False
        else:
            print(f"❌ HTTP virhe: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Yhteys epäonnistui: {e}")
        return False

def test_gpt_service():
    """Testaa GPT-palvelu"""
    print("\n🧠 TESTAA GPT-PALVELU")
    print("=" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API key löytyi")
        print("🧠 GPT käytössä - oikeat vastaukset")
        return True
    else:
        print("⚠️ OpenAI API key puuttuu")
        print("🤖 Mock-vastaukset käytössä")
        return False

def test_database():
    """Testaa tietokanta"""
    print("\n💾 TESTAA TIETOKANTA")
    print("=" * 40)
    
    try:
        import sqlite3
        conn = sqlite3.connect("sentinel_users.db")
        cursor = conn.cursor()
        
        # Testaa taulun olemassaolo
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            print("✅ Tietokanta löytyi")
            
            # Laske käyttäjät
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 Käyttäjiä: {user_count}")
            
            conn.close()
            return True
        else:
            print("❌ Käyttäjätaulu puuttuu")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Tietokantavirhe: {e}")
        return False

def test_dashboard():
    """Testaa dashboard"""
    print("\n📊 TESTAA DASHBOARD")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:8500', timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard käynnissä")
            print("🌐 URL: http://localhost:8500")
            return True
        else:
            print(f"❌ Dashboard HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard ei vastaa: {e}")
        return False

def main():
    """Pääfunktio"""
    print("🧪 SENTINEL 100K - JÄRJESTELMÄTESTI")
    print("=" * 50)
    print(f"⏰ Aika: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testit
    tests = [
        ("Telegram-botti", test_bot_connection),
        ("GPT-palvelu", test_gpt_service),
        ("Tietokanta", test_database),
        ("Dashboard", test_dashboard)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} testi epäonnistui: {e}")
            results.append((name, False))
    
    # Yhteenveto
    print("\n📋 TESTIEN YHTEENVETO")
    print("=" * 40)
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print()
    print(f"📊 Tulokset: {passed}/{len(results)} testiä läpäisi")
    
    if passed == len(results):
        print("🎉 KAIKKI TESTIT LÄPÄISI!")
        print("💬 Järjestelmä valmis käyttöön")
        print()
        print("🚀 KÄYTTÖOHJE:")
        print("1. Avaa Telegram")
        print("2. Etsi @Sentinel100bot")
        print("3. Lähetä /start")
        print("4. Keskustele: 'Hei Sentinel!'")
        print("5. Dashboard: http://localhost:8500")
    else:
        print("⚠️ Joitain testejä epäonnistui")
        print("🔧 Korjaa virheet ennen käyttöä")

if __name__ == "__main__":
    main() 