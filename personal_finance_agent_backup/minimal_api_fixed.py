#!/usr/bin/env python3
"""
🎯 SENTINEL 100K - MINIMAL WORKING API
Yksinkertainen API joka toimii varmasti ilman circular import -ongelmia.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import json
from datetime import datetime, timedelta

# FastAPI app
app = FastAPI(
    title="Sentinel 100K API",
    description="Personal Finance Agent API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    name: str
    password: str

class Transaction(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    date: Optional[str] = None

# In-memory storage (demo purposes)
users_db = {
    "demo@example.com": {
        "id": 1,
        "name": "Demo User",
        "email": "demo@example.com",
        "password": "DemoPass123",  # In real app, this would be hashed
        "created_at": "2024-01-01"
    }
}

transactions_db = [
    {
        "id": 1,
        "user_id": 1,
        "amount": -25.50,
        "category": "Ruoka",
        "description": "K-Market",
        "date": (datetime.now() - timedelta(days=1)).isoformat()
    },
    {
        "id": 2,
        "user_id": 1,
        "amount": 3200.00,
        "category": "Palkka",
        "description": "Kuukausipalkka",
        "date": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "id": 3,
        "user_id": 1,
        "amount": -450.00,
        "category": "Asuminen",
        "description": "Vuokra",
        "date": (datetime.now() - timedelta(days=2)).isoformat()
    }
]

# Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "🎯 Sentinel 100K API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/auth/login")
async def login(user_data: UserLogin):
    """User login"""
    user = users_db.get(user_data.email)
    
    if not user or user["password"] != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # In real app, generate JWT token
    token = f"demo_token_{user['id']}"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }

@app.post("/api/v1/auth/register")
async def register(user_data: UserRegister):
    """User registration"""
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user_id = len(users_db) + 1
    users_db[user_data.email] = {
        "id": new_user_id,
        "name": user_data.name,
        "email": user_data.email,
        "password": user_data.password,  # In real app, hash this
        "created_at": datetime.now().isoformat()
    }
    
    return {"message": "User created successfully", "user_id": new_user_id}

@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary(period_days: int = 30):
    """Get dashboard summary"""
    # Calculate summary from transactions
    recent_transactions = [
        t for t in transactions_db 
        if datetime.fromisoformat(t["date"]) > datetime.now() - timedelta(days=period_days)
    ]
    
    total_income = sum(t["amount"] for t in recent_transactions if t["amount"] > 0)
    total_expenses = sum(abs(t["amount"]) for t in recent_transactions if t["amount"] < 0)
    net_amount = total_income - total_expenses
    
    return {
        "period_days": period_days,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_amount": net_amount,
        "transaction_count": len(recent_transactions),
        "savings": {
            "total_savings": 25000,
            "monthly_change": 2800,
            "months_to_goal": 27,
            "target_date": "08/2027",
            "monthly_needed": 2083,
            "monthly_avg": 2800,
            "trend_3m": 0.15,
            "trend_6m": 0.08
        }
    }

@app.get("/api/v1/transactions/")
async def get_transactions(limit: int = 50, offset: int = 0):
    """Get transactions"""
    start = offset
    end = offset + limit
    
    return {
        "transactions": transactions_db[start:end],
        "total": len(transactions_db),
        "limit": limit,
        "offset": offset
    }

@app.post("/api/v1/transactions/")
async def create_transaction(transaction: Transaction):
    """Create new transaction"""
    new_transaction = {
        "id": len(transactions_db) + 1,
        "user_id": 1,  # Demo user
        "amount": transaction.amount,
        "category": transaction.category,
        "description": transaction.description,
        "date": transaction.date or datetime.now().isoformat()
    }
    
    transactions_db.append(new_transaction)
    return new_transaction

@app.get("/api/v1/guardian/status")
async def get_guardian_status():
    """Get Guardian AI status"""
    return {
        "status": "active",
        "mood_score": 75,
        "last_check": datetime.now().isoformat(),
        "alerts": [],
        "recommendations": [
            "Kuukausittaiset ruokakulut ovat 15% budjetin yli",
            "Hyvä säästötahti - jatka samaan malliin!"
        ]
    }

@app.get("/api/v1/categories/")
async def get_categories():
    """Get expense categories"""
    return [
        {"id": 1, "name": "Ruoka", "type": "expense", "color": "#FF6B6B"},
        {"id": 2, "name": "Kuljetus", "type": "expense", "color": "#4ECDC4"},
        {"id": 3, "name": "Asuminen", "type": "expense", "color": "#45B7D1"},
        {"id": 4, "name": "Vapaa-aika", "type": "expense", "color": "#96CEB4"},
        {"id": 5, "name": "Palkka", "type": "income", "color": "#82E0AA"},
        {"id": 6, "name": "Freelance", "type": "income", "color": "#F8C471"},
        {"id": 7, "name": "Sijoitukset", "type": "income", "color": "#85C1E9"}
    ]

@app.get("/api/v1/mock-gpt/health")
async def mock_gpt_health():
    """Mock GPT health check"""
    return {"status": "healthy", "model": "mock-gpt-3.5-turbo"}

if __name__ == "__main__":
    print("🚀 Käynnistetään Sentinel 100K API...")
    print("📡 API dokumentaatio: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 