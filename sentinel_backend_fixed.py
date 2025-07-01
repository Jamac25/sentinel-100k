"""
Sentinel 100K - Fixed Backend for Lovable
==========================================

Korjattu versio joka kiertää SQLAlchemy ja scheduler-ongelmat.
Toimii Lovable frontendin kanssa port 8000:ssa.

python3 sentinel_backend_fixed.py
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import json
import uuid
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Sentinel 100K Backend",
    description="🚀 Fixed Sentinel backend for Lovable frontend",
    version="3.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    created_at: datetime = Field(default_factory=datetime.now)

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    description: str
    category: str
    category_name: str
    transaction_date: datetime = Field(default_factory=datetime.now)
    merchant_name: Optional[str] = None
    type: str = "expense"
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Goal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: datetime
    progress_percent: float = 0.0
    status: str = "active"

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str = "expense"
    color: str = "#3B82F6"

# In-memory storage (simulating database)
USERS = {
    "demo-user": User(
        id="demo-user",
        email="demo@sentinel100k.fi",
        name="Matti Meikäläinen"
    )
}

TRANSACTIONS = [
    Transaction(
        id="tx1", user_id="demo-user", amount=-89.50,
        description="K-Market Ruokaostokset", category="ruoka", category_name="Ruoka",
        merchant_name="K-Market", type="expense"
    ),
    Transaction(
        id="tx2", user_id="demo-user", amount=-45.00,
        description="HSL Matkakortti", category="liikenne", category_name="Liikenne", 
        merchant_name="HSL", type="expense"
    ),
    Transaction(
        id="tx3", user_id="demo-user", amount=3200.00,
        description="Palkka", category="palkka", category_name="Palkka",
        merchant_name="Työnantaja Oy", type="income"
    ),
    Transaction(
        id="tx4", user_id="demo-user", amount=-12.90,
        description="Netflix", category="viihde", category_name="Viihde",
        merchant_name="Netflix", type="expense"
    ),
    Transaction(
        id="tx5", user_id="demo-user", amount=-67.80,
        description="Prisma Ruokaostokset", category="ruoka", category_name="Ruoka",
        merchant_name="Prisma", type="expense"
    ),
    Transaction(
        id="tx6", user_id="demo-user", amount=-156.00,
        description="Sähkölasku", category="asuminen", category_name="Asuminen",
        merchant_name="Helen Oy", type="expense"
    )
]

GOALS = [
    Goal(
        id="goal1", user_id="demo-user",
        name="Hätävara 100K€", target_amount=100000.0,
        current_amount=27850.0, target_date=datetime(2025, 12, 31),
        progress_percent=27.85, status="active"
    ),
    Goal(
        id="goal2", user_id="demo-user",
        name="Kesäloma 2024", target_amount=2500.0,
        current_amount=1200.0, target_date=datetime(2024, 6, 1),
        progress_percent=48.0, status="active"
    )
]

CATEGORIES = [
    Category(id="cat1", name="Ruoka", type="expense", color="#EF4444"),
    Category(id="cat2", name="Asuminen", type="expense", color="#3B82F6"), 
    Category(id="cat3", name="Liikenne", type="expense", color="#10B981"),
    Category(id="cat4", name="Viihde", type="expense", color="#8B5CF6"),
    Category(id="cat5", name="Palkka", type="income", color="#059669"),
]

# Helper functions
def get_current_user():
    """Get demo user for simplicity"""
    return USERS["demo-user"]

def calculate_metrics(user_id: str):
    """Calculate financial metrics"""
    user_transactions = [t for t in TRANSACTIONS if t.user_id == user_id]
    
    total_income = sum(t.amount for t in user_transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in user_transactions if t.amount < 0)
    net_amount = total_income - total_expenses
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_amount": net_amount,
        "transaction_count": len(user_transactions)
    }

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 Sentinel 100K Backend - Fixed Version",
        "status": "healthy",
        "version": "3.1.0",
        "features": [
            "No SQLAlchemy conflicts",
            "No scheduler issues", 
            "Lovable frontend compatible",
            "Real-time transaction data"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.1.0",
        "database": "memory_storage",
        "services": {
            "transactions": "active",
            "goals": "active", 
            "categories": "active",
            "dashboard": "active"
        }
    }

# Dashboard API
@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary(period_days: int = Query(30)):
    """Get dashboard summary for Lovable frontend"""
    current_user = get_current_user()
    metrics = calculate_metrics(current_user.id)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    # Filter transactions by date range
    recent_transactions = [
        t for t in TRANSACTIONS 
        if t.user_id == current_user.id and start_date <= t.transaction_date <= end_date
    ]
    
    # Calculate savings rate
    savings_rate = (metrics["net_amount"] / metrics["total_income"] * 100) if metrics["total_income"] > 0 else 0
    
    # Get main goal progress
    main_goal = next((g for g in GOALS if g.user_id == current_user.id), None)
    goal_progress = main_goal.progress_percent if main_goal else 0
    
    return {
        "period_days": period_days,
        "total_income": metrics["total_income"],
        "total_expenses": metrics["total_expenses"],
        "net_amount": metrics["net_amount"],
        "transaction_count": metrics["transaction_count"],
        "avg_daily_spending": metrics["total_expenses"] / period_days if period_days > 0 else 0,
        "expense_change_percent": 0,  # Simplified
        "goal_progress": goal_progress,
        "savings_rate": round(savings_rate, 2),
        "recent_transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "description": t.description,
                "category_name": t.category_name,
                "transaction_date": t.transaction_date.isoformat(),
                "merchant_name": t.merchant_name,
                "type": t.type
            }
            for t in recent_transactions[-5:]  # Last 5 transactions
        ],
        "top_categories": [
            {"name": "Ruoka", "amount": 157.30, "percentage": 35.2},
            {"name": "Asuminen", "amount": 156.00, "percentage": 34.9},
            {"name": "Liikenne", "amount": 45.00, "percentage": 10.1},
            {"name": "Viihde", "amount": 12.90, "percentage": 2.9}
        ]
    }

# Transactions API
@app.get("/api/v1/transactions")
async def list_transactions(
    skip: int = Query(0),
    limit: int = Query(50),
    category_id: Optional[str] = Query(None)
):
    """List transactions for Lovable frontend"""
    current_user = get_current_user()
    user_transactions = [t for t in TRANSACTIONS if t.user_id == current_user.id]
    
    # Apply category filter
    if category_id:
        user_transactions = [t for t in user_transactions if t.category == category_id]
    
    # Apply pagination
    paginated = user_transactions[skip:skip + limit]
    
    return [
        {
            "id": t.id,
            "amount": t.amount,
            "description": t.description,
            "category_name": t.category_name,
            "transaction_date": t.transaction_date.isoformat(),
            "merchant_name": t.merchant_name,
            "type": t.type,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat()
        }
        for t in paginated
    ]

@app.post("/api/v1/transactions")
async def create_transaction(transaction_data: dict):
    """Create new transaction"""
    current_user = get_current_user()
    
    new_transaction = Transaction(
        user_id=current_user.id,
        amount=transaction_data.get("amount", 0),
        description=transaction_data.get("description", ""),
        category=transaction_data.get("category", "muu"),
        category_name=transaction_data.get("category", "Muu").title(),
        merchant_name=transaction_data.get("merchant_name", ""),
        type=transaction_data.get("type", "expense")
    )
    
    TRANSACTIONS.append(new_transaction)
    
    return {
        "id": new_transaction.id,
        "amount": new_transaction.amount,
        "description": new_transaction.description,
        "category_name": new_transaction.category_name,
        "transaction_date": new_transaction.transaction_date.isoformat(),
        "merchant_name": new_transaction.merchant_name,
        "type": new_transaction.type,
        "status": new_transaction.status
    }

# Goals API  
@app.get("/api/v1/dashboard/goals/progress")
async def get_goals_progress():
    """Get goals progress for Lovable frontend"""
    current_user = get_current_user()
    user_goals = [g for g in GOALS if g.user_id == current_user.id]
    
    return [
        {
            "goal_id": g.id,
            "goal_name": g.name,
            "target_amount": g.target_amount,
            "current_amount": g.current_amount,
            "progress_percent": g.progress_percent,
            "target_date": g.target_date.isoformat(),
            "status": g.status
        }
        for g in user_goals
    ]

# Categories API
@app.get("/api/v1/categories")
async def get_categories():
    """Get categories for Lovable frontend"""
    return [
        {
            "id": c.id,
            "name": c.name,
            "type": c.type,
            "color": c.color
        }
        for c in CATEGORIES
    ]

# Category breakdown
@app.get("/api/v1/dashboard/categories/breakdown")
async def get_category_breakdown(period_days: int = Query(30)):
    """Get category breakdown for analytics"""
    current_user = get_current_user()
    
    # Calculate spending by category
    category_totals = {}
    for transaction in TRANSACTIONS:
        if transaction.user_id == current_user.id and transaction.amount < 0:
            category = transaction.category_name
            category_totals[category] = category_totals.get(category, 0) + abs(transaction.amount)
    
    total_spent = sum(category_totals.values())
    
    return [
        {
            "category_name": category,
            "total_amount": amount,
            "percentage": (amount / total_spent * 100) if total_spent > 0 else 0,
            "transaction_count": len([t for t in TRANSACTIONS if t.category_name == category and t.amount < 0])
        }
        for category, amount in category_totals.items()
    ]

# Guardian status (simplified)
@app.get("/api/v1/guardian/status")
async def get_guardian_status():
    """Get Guardian status for Lovable frontend"""
    current_user = get_current_user()
    metrics = calculate_metrics(current_user.id)
    
    # Simple risk assessment
    savings_rate = (metrics["net_amount"] / metrics["total_income"] * 100) if metrics["total_income"] > 0 else 0
    
    if savings_rate > 20:
        risk_level = "low"
        status = "excellent"
        recommendations = ["Säästämisesi on erinomaisella tasolla!", "Jatka samaan malliin."]
    elif savings_rate > 10:
        risk_level = "medium"
        status = "good"
        recommendations = ["Hyvä säästämisaste.", "Voisit yrittää säästää hieman enemmän."]
    else:
        risk_level = "high"
        status = "needs_attention"
        recommendations = ["Säästämisesi kaipaa tehostamista.", "Tarkista budjettisi ja vähennä kuluja."]
    
    return {
        "status": status,
        "risk_level": risk_level,
        "monitoring": "active",
        "last_check": datetime.now().isoformat(),
        "recommendations": recommendations,
        "savings_rate": round(savings_rate, 1),
        "analysis": {
            "expense_ratio": metrics["total_expenses"] / metrics["total_income"] if metrics["total_income"] > 0 else 0,
            "savings_rate": savings_rate / 100,
            "financial_health": status
        }
    }

# AI Chat (simplified responses)
@app.post("/api/v1/chat")
async def ai_chat(message: dict):
    """AI Chat for Lovable frontend"""
    user_message = message.get("message", "").lower()
    current_user = get_current_user()
    metrics = calculate_metrics(current_user.id)
    
    # Context-aware responses
    if "säästä" in user_message:
        response = f"💡 Sinulla on {metrics['net_amount']:.0f}€ säästöjä. Suosittelen automaattista säästämistä - aseta 20% tuloistasi suoraan säästötilille!"
    elif "budjetti" in user_message:
        response = f"📊 Kuluja sinulla on {metrics['total_expenses']:.0f}€. Kokeile 50/30/20 sääntöä: 50% välttämättömyyksiin, 30% haluihin, 20% säästöihin."
    elif "sijoitus" in user_message:
        response = "📈 Kun sinulla on hätävarat kunnossa, aloita indeksirahastoilla. Ne ovat turvallisia ja edullisia!"
    elif "tavoite" in user_message:
        main_goal = next((g for g in GOALS if g.user_id == current_user.id), None)
        if main_goal:
            response = f"🎯 100K€ tavoitteessasi olet {main_goal.progress_percent:.1f}% valmis! Loistavaa työtä!"
        else:
            response = "🎯 Aseta itsellesi säästötavoite - se motivoi säästämään!"
    else:
        response = f"Kiitos kysymyksestäsi! Voin auttaa säästämisessä, budjetoinnissa ja sijoittamisessa. Sinulla on {metrics['net_amount']:.0f}€ säästöjä."
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "confidence": 0.9,
        "type": "financial_advice",
        "user_context": {
            "savings": metrics["net_amount"],
            "income": metrics["total_income"],
            "expenses": metrics["total_expenses"]
        }
    }

# Auth endpoints (simplified)
@app.get("/api/v1/auth/me")
async def get_current_user_info():
    """Get current user info"""
    user = get_current_user()
    metrics = calculate_metrics(user.id)
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at.isoformat(),
        "current_savings": metrics["net_amount"],
        "savings_goal": 100000.0
    }

if __name__ == "__main__":
    print("🚀 Starting Fixed Sentinel 100K Backend")
    print("📊 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🎨 Lovable Compatible: ✅")
    print("💾 Storage: In-memory (no database conflicts)")
    print("🔧 Scheduler: Disabled (no serialization issues)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 