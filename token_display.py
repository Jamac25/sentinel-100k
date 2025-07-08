#!/usr/bin/env python3
"""
TELEGRAM TOKEN DISPLAY - For webhook setup
"""
import os

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return
    
    print("🤖 TELEGRAM BOT TOKEN FOUND!")
    print(f"Token: {token}")
    print()
    print("🔗 WEBHOOK SETUP COMMANDS:")
    print(f"curl \"https://api.telegram.org/bot{token}/setWebhook?url=https://sentinel-100k.onrender.com/telegram/webhook\"")
    print()
    print("📋 TEST COMMANDS:")
    print(f"curl \"https://api.telegram.org/bot{token}/getMe\"")
    print(f"curl \"https://api.telegram.org/bot{token}/getWebhookInfo\"")
    print()
    print("✅ Copy the setWebhook command and run it!")

if __name__ == "__main__":
    main() 