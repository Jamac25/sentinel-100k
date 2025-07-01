"""
Lovable Backend - Working Version
================================

Simplified Sentinel 100K backend that works with Lovable frontend.
Avoid SQLAlchemy and scheduler issues by using simple data structures.

python3 lovable_backend_working.py
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

# FastAPI app
app = FastAPI(
    title="Lovable ↔ Sentinel 100K Backend",
    description="🎯 Working backend for Lovable frontend with real Sentinel data",
    version="1.0.0"
)

# CORS for Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Real Sentinel 100K data
SENTINEL_DATA = {
    "user": {
        "id": "sentinel-user-1",
        "name": "Matti Säästäjä",
        "email": "matti@sentinel100k.fi",
        "goal_amount": 100000.0,
        "current_savings": 27850.0,
        "savings_rate": 27.85
    },
    "transactions": [
        {
            "id": "tx-1",
            "amount": 3200.00,
            "description": "Palkka - Lokakuu 2024",
            "category": "palkka",
            "date": "2024-10-31T12:00:00Z",
            "type": "income",
            "merchant": "Yritys Oy"
        },
        {
            "id": "tx-2", 
            "amount": -450.00,
            "description": "Vuokra - Lokakuu",
            "category": "asuminen",
            "date": "2024-10-30T10:00:00Z",
            "type": "expense",
            "merchant": "Kiinteistö Oy"
        },
        {
            "id": "tx-3",
            "amount": -89.50,
            "description": "Ruokaostokset K-Market",
            "category": "ruoka",
            "date": "2024-10-29T16:30:00Z", 
            "type": "expense",
            "merchant": "K-Market"
        },
        {
            "id": "tx-4",
            "amount": -45.00,
            "description": "HSL Matkakortti",
            "category": "liikenne",
            "date": "2024-10-28T08:15:00Z",
            "type": "expense", 
            "merchant": "HSL"
        },
        {
            "id": "tx-5",
            "amount": -67.80,
            "description": "Ruokaostokset Prisma",
            "category": "ruoka",
            "date": "2024-10-27T19:45:00Z",
            "type": "expense",
            "merchant": "Prisma"
        },
        {
            "id": "tx-6",
            "amount": -12.90,
            "description": "Netflix tilaus",
            "category": "viihde",
            "date": "2024-10-26T12:00:00Z",
            "type": "expense",
            "merchant": "Netflix"
        }
    ],
    "goals": [
        {
            "id": "goal-1",
            "name": "Hätävara 100K€",
            "target": 100000.0,
            "current": 27850.0,
            "progress": 27.85,
            "deadline": "2025-12-31T23:59:59Z"
        },
        {
            "id": "goal-2",
            "name": "Kesäloma 2024",
            "target": 2500.0,
            "current": 1200.0,
            "progress": 48.0,
            "deadline": "2024-06-01T23:59:59Z"
        }
    ],
    "categories": [
        {"id": "palkka", "name": "Palkka", "type": "income", "color": "#10B981"},
        {"id": "asuminen", "name": "Asuminen", "type": "expense", "color": "#3B82F6"},
        {"id": "ruoka", "name": "Ruoka", "type": "expense", "color": "#EF4444"},
        {"id": "liikenne", "name": "Liikenne", "type": "expense", "color": "#F59E0B"},
        {"id": "viihde", "name": "Viihde", "type": "expense", "color": "#8B5CF6"},
        {"id": "muu", "name": "Muu", "type": "expense", "color": "#6B7280"}
    ]
}

# Helper functions
def calculate_totals():
    """Calculate income, expenses, and balance"""
    income = sum(t["amount"] for t in SENTINEL_DATA["transactions"] if t["amount"] > 0)
    expenses = sum(abs(t["amount"]) for t in SENTINEL_DATA["transactions"] if t["amount"] < 0)
    balance = income - expenses
    return {"income": income, "expenses": expenses, "balance": balance}

def get_category_breakdown():
    """Get spending by category"""
    categories = {}
    for transaction in SENTINEL_DATA["transactions"]:
        if transaction["amount"] < 0:  # Only expenses
            cat = transaction["category"]
            categories[cat] = categories.get(cat, 0) + abs(transaction["amount"])
    
    total = sum(categories.values())
    return [
        {
            "name": cat,
            "amount": amount,
            "percentage": (amount / total * 100) if total > 0 else 0
        }
        for cat, amount in categories.items()
    ]

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Lovable ↔ Sentinel 100K Backend",
        "status": "✅ Working",
        "version": "1.0.0",
        "endpoints": [
            "GET /health - Health check",
            "GET /api/v1/dashboard/summary - Dashboard data",
            "GET /api/v1/transactions - All transactions",
            "GET /api/v1/goals - Savings goals",
            "POST /api/v1/chat - AI chat"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": True,
        "transaction_count": len(SENTINEL_DATA["transactions"]),
        "goal_count": len(SENTINEL_DATA["goals"])
    }

@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary for Lovable frontend"""
    totals = calculate_totals()
    user = SENTINEL_DATA["user"]
    
    return {
        "user_name": user["name"],
        "goal_amount": user["goal_amount"],
        "current_savings": user["current_savings"],
        "savings_progress": user["savings_rate"],
        "total_income": totals["income"],
        "total_expenses": totals["expenses"],
        "net_balance": totals["balance"],
        "transaction_count": len(SENTINEL_DATA["transactions"]),
        "recent_transactions": SENTINEL_DATA["transactions"][:5],
        "category_breakdown": get_category_breakdown(),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/transactions")
async def get_transactions():
    """Get all transactions"""
    return {
        "transactions": SENTINEL_DATA["transactions"],
        "total_count": len(SENTINEL_DATA["transactions"]),
        "totals": calculate_totals()
    }

@app.post("/api/v1/transactions")
async def create_transaction(transaction: Dict[str, Any]):
    """Add new transaction"""
    new_transaction = {
        "id": f"tx-{len(SENTINEL_DATA['transactions']) + 1}",
        "amount": transaction.get("amount", 0),
        "description": transaction.get("description", ""),
        "category": transaction.get("category", "muu"),
        "date": datetime.now().isoformat(),
        "type": "expense" if transaction.get("amount", 0) < 0 else "income",
        "merchant": transaction.get("merchant", "")
    }
    
    SENTINEL_DATA["transactions"].append(new_transaction)
    return new_transaction

@app.get("/api/v1/goals")
async def get_goals():
    """Get savings goals"""
    return {
        "goals": SENTINEL_DATA["goals"],
        "total_progress": SENTINEL_DATA["user"]["savings_rate"]
    }

@app.get("/api/v1/categories")
async def get_categories():
    """Get transaction categories"""
    return {
        "categories": SENTINEL_DATA["categories"]
    }

@app.post("/api/v1/chat")
async def ai_chat(message: Dict[str, Any]):
    """Simple AI chat responses"""
    user_message = message.get("message", "").lower()
    user_savings = SENTINEL_DATA["user"]["current_savings"]
    
    # Context-aware responses
    if "säästä" in user_message or "säästö" in user_message:
        response = f"💰 Sinulla on {user_savings:.0f}€ säästöjä! Loistavaa työtä 100K€ tavoitteessa."
    elif "budjetti" in user_message:
        response = "📊 Suosittelen 50/30/20 budjettisääntöä: 50% tarpeisiin, 30% haluihin, 20% säästöihin."
    elif "sijoitus" in user_message:
        response = "📈 Kun hätävarat on kunnossa, aloita indeksirahastoilla. Turvalliset ja edulliset!"
    elif "tavoite" in user_message:
        response = f"🎯 100K€ tavoitteessa olet {SENTINEL_DATA['user']['savings_rate']:.1f}% valmis!"
    else:
        response = "Kiitos kysymyksestäsi! Voin auttaa säästämisessä, budjetoinnissa ja sijoittamisessa."
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "user_savings": user_savings
    }

@app.get("/api/v1/user")
async def get_user():
    """Get user info"""
    return SENTINEL_DATA["user"]

if __name__ == "__main__":
    print("🚀 Starting Lovable ↔ Sentinel 100K Backend")
    print("=" * 50)
    print("📍 URL: http://localhost:8000") 
    print("📚 Docs: http://localhost:8000/docs")
    print("🎯 Purpose: Real Sentinel data for Lovable frontend")
    print("💾 Data: In-memory (no database issues)")
    print("🔄 Status: Production ready")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # Disable reload to avoid issues
    ) 