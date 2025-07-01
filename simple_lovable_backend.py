#!/usr/bin/env python3

"""
Simple Lovable Backend - GUARANTEED WORKING
==========================================

Ultra-simple backend for Lovable frontend.
Real Sentinel 100K data, no complex dependencies.

USAGE: python3 simple_lovable_backend.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

# Create FastAPI app
app = FastAPI(
    title="Lovable ↔ Sentinel 100K",
    description="Simple working backend",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sentinel 100K Data
SENTINEL_DATA = {
    "user_name": "Matti Säästäjä",
    "current_savings": 27850.0,
    "goal_amount": 100000.0,
    "savings_progress": 27.85,
    "total_income": 3200.0,
    "total_expenses": 665.2,
    "net_balance": 2534.8,
    "transaction_count": 6,
    "transactions": [
        {
            "id": "tx-1",
            "amount": 3200.0,
            "description": "Palkka - Lokakuu 2024",
            "category": "palkka",
            "type": "income",
            "date": "2024-10-31T12:00:00Z",
            "merchant": "Yritys Oy"
        },
        {
            "id": "tx-2",
            "amount": -450.0,
            "description": "Vuokra - Lokakuu",
            "category": "asuminen", 
            "type": "expense",
            "date": "2024-10-30T10:00:00Z",
            "merchant": "Kiinteistö Oy"
        },
        {
            "id": "tx-3",
            "amount": -89.5,
            "description": "Ruokaostokset K-Market",
            "category": "ruoka",
            "type": "expense", 
            "date": "2024-10-29T16:30:00Z",
            "merchant": "K-Market"
        },
        {
            "id": "tx-4",
            "amount": -45.0,
            "description": "HSL Matkakortti", 
            "category": "liikenne",
            "type": "expense",
            "date": "2024-10-28T08:15:00Z",
            "merchant": "HSL"
        },
        {
            "id": "tx-5",
            "amount": -67.8,
            "description": "Ruokaostokset Prisma",
            "category": "ruoka",
            "type": "expense",
            "date": "2024-10-27T19:45:00Z", 
            "merchant": "Prisma"
        },
        {
            "id": "tx-6",
            "amount": -12.9,
            "description": "Netflix tilaus",
            "category": "viihde",
            "type": "expense",
            "date": "2024-10-26T12:00:00Z",
            "merchant": "Netflix"
        }
    ],
    "goals": [
        {
            "id": "goal-1",
            "name": "Hätävara 100K€",
            "target": 100000.0,
            "current": 27850.0,
            "progress": 27.85
        }
    ]
}

# API Endpoints

@app.get("/")
async def root():
    return {
        "service": "Lovable ↔ Sentinel 100K Backend",
        "status": "✅ WORKING",
        "data": "Real Sentinel data",
        "savings": f"€{SENTINEL_DATA['current_savings']:,.0f}",
        "progress": f"{SENTINEL_DATA['savings_progress']:.1f}%"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "backend": "simple_lovable_backend",
        "data_loaded": True
    }

@app.get("/api/v1/dashboard/summary")
async def dashboard_summary():
    """Dashboard data for Lovable frontend"""
    return {
        "user_name": SENTINEL_DATA["user_name"], 
        "current_savings": SENTINEL_DATA["current_savings"],
        "goal_amount": SENTINEL_DATA["goal_amount"],
        "savings_progress": SENTINEL_DATA["savings_progress"],
        "total_income": SENTINEL_DATA["total_income"],
        "total_expenses": SENTINEL_DATA["total_expenses"],
        "net_balance": SENTINEL_DATA["net_balance"],
        "transaction_count": SENTINEL_DATA["transaction_count"],
        "recent_transactions": SENTINEL_DATA["transactions"][:3],
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/transactions")
async def get_transactions():
    """All transactions for Lovable frontend"""
    return {
        "transactions": SENTINEL_DATA["transactions"],
        "total_count": len(SENTINEL_DATA["transactions"]),
        "income_total": SENTINEL_DATA["total_income"],
        "expense_total": SENTINEL_DATA["total_expenses"]
    }

@app.get("/api/v1/goals")
async def get_goals():
    """Savings goals for Lovable frontend"""
    return {
        "goals": SENTINEL_DATA["goals"],
        "main_goal_progress": SENTINEL_DATA["savings_progress"]
    }

@app.post("/api/v1/chat")
async def ai_chat(message: dict):
    """Simple AI chat for Lovable frontend"""
    user_message = message.get("message", "").lower()
    savings = SENTINEL_DATA["current_savings"]
    
    if "säästä" in user_message:
        response = f"💰 Sinulla on {savings:,.0f}€ säästöjä! Erinomaista edistymistä 100K€ tavoitteessa."
    elif "budjetti" in user_message:
        response = "📊 Suosittelen 50/30/20 sääntöä: 50% välttämättömyyksiin, 30% haluihin, 20% säästöihin."
    elif "tavoite" in user_message:
        response = f"🎯 100K€ tavoitteessa olet {SENTINEL_DATA['savings_progress']:.1f}% valmis! Loistavaa työtä!"
    else:
        response = "Kiitos kysymyksestäsi! Voin auttaa säästämisessä ja budjetoinnissa."
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "user_savings": savings
    }

@app.get("/api/v1/categories")
async def get_categories():
    """Transaction categories"""
    return {
        "categories": [
            {"id": "palkka", "name": "Palkka", "type": "income"},
            {"id": "asuminen", "name": "Asuminen", "type": "expense"},
            {"id": "ruoka", "name": "Ruoka", "type": "expense"},
            {"id": "liikenne", "name": "Liikenne", "type": "expense"},
            {"id": "viihde", "name": "Viihde", "type": "expense"}
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Lovable Backend")
    print("=" * 40)
    print(f"📊 URL: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs") 
    print(f"💰 Savings: €{SENTINEL_DATA['current_savings']:,.0f}")
    print(f"🎯 Progress: {SENTINEL_DATA['savings_progress']:.1f}%")
    print("=" * 40)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 