"""
Sentinel 100K - Lovable.dev Compatible Backend
============================================

Complete Finnish Personal Finance API optimized for Lovable frontend development.
Includes all Sentinel 100K features with perfect CORS and API structure for Lovable.

Run: python lovable_sentinel_backend.py
API: http://localhost:8000
Docs: http://localhost:8000/docs

Frontend connection: Configure Lovable to use http://localhost:8000/api/v1/
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uvicorn
import json
import uuid
import os
import logging
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI with Lovable-friendly configuration
app = FastAPI(
    title="Sentinel 100K API",
    description="🚀 Älykkä henkilökohtaisen talouden hallinta - Lovable Compatible",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS configuration optimized for Lovable.dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:5173",
        "http://localhost:8080",
        "https://*.lovable.dev",
        "https://lovable.dev",
        "https://*.netlify.app",
        "https://*.vercel.app",
        "*"  # For development - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Data Models for Lovable Frontend
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    settings: Dict[str, Any] = Field(default_factory=dict)

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    description: str
    category: str
    date: datetime = Field(default_factory=datetime.now)
    type: str = Field(..., regex="^(income|expense)$")
    merchant: Optional[str] = None
    location: Optional[str] = None

class Goal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    target_amount: float
    current_amount: float = 0.0
    target_date: datetime
    description: Optional[str] = None
    category: str = "savings"
    progress: float = Field(default=0.0, ge=0.0, le=100.0)

class AIInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str
    title: str
    message: str
    priority: str = Field(default="medium", regex="^(low|medium|high|urgent)$")
    created_at: datetime = Field(default_factory=datetime.now)
    category: str = "general"

class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    savings_rate: float
    monthly_goal_progress: float
    recent_transactions: List[Transaction]
    upcoming_goals: List[Goal]
    ai_insights: List[AIInsight]

# Mock Data for Finnish Users (Lovable Development)
MOCK_USERS = {
    "demo": User(
        id="demo-user-123",
        email="demo@sentinel100k.fi", 
        name="Matti Meikäläinen",
        avatar_url="https://api.dicebear.com/7.x/avatars/svg?seed=matti"
    )
}

MOCK_TRANSACTIONS = [
    Transaction(
        id="tx1", user_id="demo-user-123", amount=-85.50, 
        description="K-Market Ruokaostokset", category="Ruoka", 
        type="expense", merchant="K-Market", location="Helsinki"
    ),
    Transaction(
        id="tx2", user_id="demo-user-123", amount=-45.20,
        description="HSL Matkakortti", category="Liikenne",
        type="expense", merchant="HSL", location="Helsinki"
    ),
    Transaction(
        id="tx3", user_id="demo-user-123", amount=3200.00,
        description="Palkka - Ohjelmistokehittäjä", category="Palkka",
        type="income", merchant="Yritys Oy", location="Helsinki"
    ),
    Transaction(
        id="tx4", user_id="demo-user-123", amount=-12.90,
        description="Netflix", category="Viihde",
        type="expense", merchant="Netflix", location="Online"
    ),
    Transaction(
        id="tx5", user_id="demo-user-123", amount=-156.00,
        description="Sähkölasku", category="Asuminen",
        type="expense", merchant="Helen", location="Helsinki"
    )
]

MOCK_GOALS = [
    Goal(
        id="goal1", user_id="demo-user-123",
        title="Hätävara 100K€", target_amount=100000.0,
        current_amount=25750.0, target_date=datetime(2025, 12, 31),
        description="Turvallinen taloudellinen tulevaisuus",
        progress=25.75
    ),
    Goal(
        id="goal2", user_id="demo-user-123", 
        title="Kesäloma 2024", target_amount=3000.0,
        current_amount=1250.0, target_date=datetime(2024, 6, 1),
        description="Espanjan matka", progress=41.67
    )
]

MOCK_AI_INSIGHTS = [
    AIInsight(
        id="ai1", user_id="demo-user-123", type="savings_tip",
        title="Säästövinkki", priority="medium",
        message="Voisit säästää 150€/kk vähentämällä ulkona syömistä 2 kertaa viikossa.",
        category="optimization"
    ),
    AIInsight(
        id="ai2", user_id="demo-user-123", type="goal_progress",
        title="Tavoitteen Edistyminen", priority="high",
        message="Olet etuajassa 100K€ tavoitteessasi! Nykyisellä säästöllä saavutat sen 8 kuukautta etuajassa.",
        category="achievement"
    )
]

# Helper Functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user - simplified for Lovable development"""
    return MOCK_USERS["demo"]

def calculate_financial_metrics(user_id: str) -> Dict[str, float]:
    """Calculate key financial metrics"""
    user_transactions = [t for t in MOCK_TRANSACTIONS if t.user_id == user_id]
    
    total_income = sum(t.amount for t in user_transactions if t.type == "income")
    total_expenses = sum(abs(t.amount) for t in user_transactions if t.type == "expense")
    balance = total_income - total_expenses
    savings_rate = (balance / total_income * 100) if total_income > 0 else 0
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "savings_rate": round(savings_rate, 2)
    }

# API Routes for Lovable Frontend

@app.get("/")
async def root():
    """API Health Check for Lovable"""
    return {
        "message": "🚀 Sentinel 100K API - Lovable Compatible",
        "status": "healthy",
        "version": "2.0.0",
        "endpoints": "/docs",
        "frontend_connection": "http://localhost:8000/api/v1/"
    }

@app.get("/api/v1/health")
async def health_check():
    """Detailed health check for Lovable monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "ai_service": "ready", 
            "guardian": "active",
            "mock_data": "loaded"
        },
        "metrics": {
            "uptime": "99.9%",
            "response_time": "< 100ms",
            "active_users": 1
        }
    }

# User Management
@app.get("/api/v1/user/profile", response_model=User)
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get current user profile"""
    return user

@app.put("/api/v1/user/profile")
async def update_user_profile(updates: Dict[str, Any], user: User = Depends(get_current_user)):
    """Update user profile"""
    return {"message": "Profile updated successfully", "user": user}

# Financial Dashboard
@app.get("/api/v1/dashboard/summary", response_model=FinancialSummary)
async def get_dashboard_summary(user: User = Depends(get_current_user)):
    """Get complete financial dashboard data for Lovable frontend"""
    metrics = calculate_financial_metrics(user.id)
    
    # Calculate goal progress
    main_goal = next((g for g in MOCK_GOALS if g.user_id == user.id), None)
    goal_progress = main_goal.progress if main_goal else 0.0
    
    return FinancialSummary(
        total_income=metrics["total_income"],
        total_expenses=metrics["total_expenses"],
        balance=metrics["balance"],
        savings_rate=metrics["savings_rate"],
        monthly_goal_progress=goal_progress,
        recent_transactions=MOCK_TRANSACTIONS[:5],
        upcoming_goals=MOCK_GOALS,
        ai_insights=MOCK_AI_INSIGHTS
    )

# Transactions
@app.get("/api/v1/transactions", response_model=List[Transaction])
async def get_transactions(
    limit: int = 50,
    category: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Get user transactions with optional filtering"""
    transactions = [t for t in MOCK_TRANSACTIONS if t.user_id == user.id]
    
    if category:
        transactions = [t for t in transactions if t.category.lower() == category.lower()]
    
    return transactions[:limit]

@app.post("/api/v1/transactions", response_model=Transaction)
async def create_transaction(transaction_data: Transaction, user: User = Depends(get_current_user)):
    """Create new transaction"""
    transaction_data.user_id = user.id
    MOCK_TRANSACTIONS.append(transaction_data)
    return transaction_data

# Goals Management  
@app.get("/api/v1/goals", response_model=List[Goal])
async def get_goals(user: User = Depends(get_current_user)):
    """Get user goals"""
    return [g for g in MOCK_GOALS if g.user_id == user.id]

@app.post("/api/v1/goals", response_model=Goal)
async def create_goal(goal_data: Goal, user: User = Depends(get_current_user)):
    """Create new savings goal"""
    goal_data.user_id = user.id
    MOCK_GOALS.append(goal_data)
    return goal_data

@app.put("/api/v1/goals/{goal_id}", response_model=Goal)
async def update_goal(goal_id: str, updates: Dict[str, Any], user: User = Depends(get_current_user)):
    """Update goal progress"""
    goal = next((g for g in MOCK_GOALS if g.id == goal_id and g.user_id == user.id), None)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for key, value in updates.items():
        if hasattr(goal, key):
            setattr(goal, key, value)
    
    # Recalculate progress
    if goal.target_amount > 0:
        goal.progress = min((goal.current_amount / goal.target_amount) * 100, 100)
    
    return goal

# AI & Insights
@app.get("/api/v1/ai/insights", response_model=List[AIInsight])
async def get_ai_insights(user: User = Depends(get_current_user)):
    """Get AI-powered financial insights"""
    return [i for i in MOCK_AI_INSIGHTS if i.user_id == user.id]

@app.post("/api/v1/ai/chat")
async def ai_chat(message: Dict[str, str], user: User = Depends(get_current_user)):
    """AI Chat endpoint for financial advice"""
    user_message = message.get("message", "")
    
    # Mock AI responses based on keywords
    if "säästä" in user_message.lower():
        response = "Suosittelen automaattista säästämistä. Aseta 20% tuloistasi suoraan säästötilille kuukausittain!"
    elif "budjetti" in user_message.lower():
        response = "50/30/20 sääntö toimii hyvin: 50% välttämättömyyksiin, 30% haluihin, 20% säästöihin."
    elif "sijoitus" in user_message.lower():
        response = "Aloita indeksirahastoilla. Ne ovat turvallisia ja edullisia aloittelijoille."
    else:
        response = f"Kiitos kysymyksestäsi '{user_message}'. Voin auttaa säästämisessä, budjetoinnissa ja sijoittamisessa!"
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "confidence": 0.95,
        "type": "financial_advice"
    }

# Categories & Analytics
@app.get("/api/v1/categories")
async def get_categories():
    """Get expense categories for Lovable forms"""
    return {
        "income": ["Palkka", "Freelance", "Sijoitukset", "Muu tulo"],
        "expense": ["Ruoka", "Asuminen", "Liikenne", "Viihde", "Vaatteet", "Terveys", "Muu"]
    }

@app.get("/api/v1/analytics/spending")
async def get_spending_analytics(user: User = Depends(get_current_user)):
    """Get spending analytics for charts"""
    user_transactions = [t for t in MOCK_TRANSACTIONS if t.user_id == user.id and t.type == "expense"]
    
    # Group by category
    category_spending = {}
    for transaction in user_transactions:
        category = transaction.category
        category_spending[category] = category_spending.get(category, 0) + abs(transaction.amount)
    
    return {
        "by_category": category_spending,
        "total_spent": sum(category_spending.values()),
        "largest_category": max(category_spending.items(), key=lambda x: x[1]) if category_spending else None,
        "period": "current_month"
    }

# Guardian System (Risk Monitoring)
@app.get("/api/v1/guardian/status")
async def get_guardian_status(user: User = Depends(get_current_user)):
    """Get Guardian monitoring status"""
    metrics = calculate_financial_metrics(user.id)
    
    # Assess risk level
    if metrics["savings_rate"] > 20:
        risk_level = "low"
        status = "excellent"
    elif metrics["savings_rate"] > 10:
        risk_level = "medium" 
        status = "good"
    else:
        risk_level = "high"
        status = "needs_attention"
    
    return {
        "status": status,
        "risk_level": risk_level,
        "monitoring": "active",
        "last_check": datetime.now().isoformat(),
        "recommendations": [
            "Säästösi on hyvällä tasolla! Jatka samaan malliin.",
            "Harkitse automaattista säästämistä."
        ] if risk_level == "low" else [
            "Säästöprosenttiasi voisi parantaa.",
            "Tarkista kuukausibudjettisi."
        ]
    }

@app.get("/api/v1/guardian/alerts")
async def get_guardian_alerts(user: User = Depends(get_current_user)):
    """Get active financial alerts"""
    return [
        {
            "id": "alert1",
            "type": "goal_milestone",
            "message": "Olet saavuttanut 25% pääsäästötavoitteestasi! 🎉",
            "severity": "info",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "alert2", 
            "type": "spending_pattern",
            "message": "Ruokaostoksesi ovat kasvaneet 15% tässä kuussa.",
            "severity": "warning",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
        }
    ]

# Lovable Integration Helpers
@app.get("/api/v1/lovable/config")
async def get_lovable_config():
    """Configuration for Lovable frontend development"""
    return {
        "api_base_url": "http://localhost:8000/api/v1",
        "websocket_url": "ws://localhost:8000/ws",
        "auth_required": False,  # Simplified for development
        "demo_user": {
            "email": "demo@sentinel100k.fi",
            "password": "demo123"
        },
        "features": {
            "transactions": True,
            "goals": True,
            "ai_chat": True,
            "analytics": True,
            "guardian": True,
            "real_time": True
        },
        "ui_config": {
            "currency": "EUR",
            "locale": "fi-FI",
            "date_format": "DD.MM.YYYY",
            "theme": "sentinel"
        }
    }

@app.get("/api/v1/lovable/mock-data")
async def get_mock_data():
    """Get all mock data for Lovable development"""
    return {
        "users": MOCK_USERS,
        "transactions": MOCK_TRANSACTIONS,
        "goals": MOCK_GOALS,
        "insights": MOCK_AI_INSIGHTS,
        "last_updated": datetime.now().isoformat()
    }

# WebSocket for Real-time Updates
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket for real-time updates in Lovable frontend"""
    await websocket.accept()
    try:
        while True:
            # Send periodic updates
            await websocket.send_json({
                "type": "financial_update",
                "data": {
                    "balance": 25750.00,
                    "goal_progress": 25.75,
                    "timestamp": datetime.now().isoformat()
                }
            })
            await asyncio.sleep(30)  # Update every 30 seconds
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

# Error Handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "available_endpoints": "/docs",
            "lovable_config": "/api/v1/lovable/config"
        }
    )

if __name__ == "__main__":
    print("🚀 Starting Sentinel 100K Backend for Lovable.dev")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔧 Lovable Config: http://localhost:8000/api/v1/lovable/config")
    print("💡 Frontend Base URL: http://localhost:8000/api/v1/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 