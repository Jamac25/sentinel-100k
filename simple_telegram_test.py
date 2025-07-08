#!/usr/bin/env python3
"""
SIMPLE TELEGRAM TEST - RENDER DEBUG + TOKEN CHECK
"""
import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="Telegram Token Test", version="TEST.2.0")

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None

@app.get("/")
def root():
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    return {
        "status": "TELEGRAM_TOKEN_TEST_ACTIVE", 
        "version": "TEST.2.0",
        "telegram_token_set": bool(telegram_token),
        "token_length": len(telegram_token) if telegram_token else 0,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/token/test")
def test_token():
    """Test if Telegram token works"""
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not telegram_token:
        return {
            "status": "error",
            "message": "TELEGRAM_BOT_TOKEN not found in environment",
            "solution": "Add TELEGRAM_BOT_TOKEN to Render environment variables"
        }
    
    # Test token with Telegram API
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            return {
                "status": "success",
                "message": "Telegram token is VALID!",
                "bot_info": bot_info.get("result", {}),
                "token_working": True
            }
        else:
            return {
                "status": "error", 
                "message": f"Token invalid - Telegram API returned {response.status_code}",
                "response": response.text[:200]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to test token: {str(e)}",
            "solution": "Check token format and network connection"
        }

@app.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Test webhook endpoint"""
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if update.message:
        chat_id = update.message.get("chat", {}).get("id")
        text = update.message.get("text", "")
        username = update.message.get("from", {}).get("username", "Unknown")
        
        # Simple test response
        response_text = f"🤖 TEST VASTAUS: Hei {username}! Sain viestisi: '{text}'. Token toimii!"
        
        if telegram_token:
            try:
                telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": response_text
                }
                
                response = requests.post(telegram_url, json=payload)
                return {
                    "status": "success" if response.status_code == 200 else "error",
                    "telegram_response_code": response.status_code,
                    "message": f"Webhook processed for {username}"
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "no_token", "message": "Token missing"}
    
    return {"status": "TELEGRAM_WEBHOOK_WORKING", "test": True}

@app.get("/telegram/webhook")
async def telegram_webhook_get():
    return {"status": "TELEGRAM_GET_WORKING", "test": True}

@app.get("/webhook/setup")
def webhook_setup_guide():
    """Guide for setting up webhook"""
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    base_url = "https://sentinel-100k.onrender.com"
    
    if not telegram_token:
        return {
            "status": "error",
            "message": "Set TELEGRAM_BOT_TOKEN first!"
        }
    
    webhook_url = f"{base_url}/telegram/webhook"
    set_webhook_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook?url={webhook_url}"
    
    return {
        "status": "ready",
        "webhook_url": webhook_url,
        "setup_command": f"curl '{set_webhook_url}'",
        "test_command": f"curl {base_url}/token/test",
        "steps": [
            "1. Set TELEGRAM_BOT_TOKEN in Render environment",
            "2. Deploy the app",
            f"3. Run: curl '{set_webhook_url}'",
            "4. Send message to your bot in Telegram",
            "5. Check if bot responds"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 