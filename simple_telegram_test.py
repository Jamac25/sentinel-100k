#!/usr/bin/env python3
"""
SIMPLE TELEGRAM TEST - RENDER DEBUG
"""
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="Telegram Test", version="TEST.1.0")

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None

@app.get("/")
def root():
    return {"status": "TELEGRAM_TEST_ACTIVE", "version": "TEST.1.0"}

@app.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate):
    return {"status": "TELEGRAM_WEBHOOK_WORKING", "test": True}

@app.get("/telegram/webhook")
async def telegram_webhook_get():
    return {"status": "TELEGRAM_GET_WORKING", "test": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 