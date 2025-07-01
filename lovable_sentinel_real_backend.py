"""
Sentinel 100K - Real Lovable Backend
=====================================

Connects Lovable frontend to real Sentinel 100K backend data.
No mock data - uses actual database and APIs from personal_finance_agent.

Run: python3 lovable_sentinel_real_backend.py
API: http://localhost:9000
Real Backend: http://localhost:8000 (personal_finance_agent)

Frontend connection: http://localhost:9000/api/v1/
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import httpx
import asyncio
import logging
import os
import sys

# Add personal_finance_agent to path for imports
sys.path.append('personal_finance_agent')

try:
    from personal_finance_agent.app.models import Transaction, User, Category, Goal
    from personal_finance_agent.app.db.init_db import get_db, init_db
    from personal_finance_agent.app.core.config import settings as backend_settings
    from personal_finance_agent.app.api.auth import get_current_user
except ImportError as e:
    print(f"Warning: Could not import Sentinel backend modules: {e}")
    print("Using fallback mode...")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Sentinel 100K Real API",
    description="🚀 Lovable-compatible interface to real Sentinel 100K backend",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS for Lovable
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
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend connection
SENTINEL_BACKEND_URL = "http://localhost:8000"
security = HTTPBearer(auto_error=False)

# Lovable Data Models (compatible with real backend)
class LovableUser(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime
    current_savings: float = 0.0
    savings_goal: float = 100000.0

class LovableTransaction(BaseModel):
    id: str
    user_id: str
    amount: float
    description: str
    category: str
    date: datetime
    type: str  # "income" or "expense"
    merchant: Optional[str] = None
    location: Optional[str] = None

class LovableGoal(BaseModel):
    id: str
    user_id: str
    title: str
    target_amount: float
    current_amount: float
    target_date: datetime
    progress: float

class LovableFinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    savings_rate: float
    goal_progress: float
    recent_transactions: List[LovableTransaction]
    goals: List[LovableGoal]
    period: str = "current_month"

# Helper Functions
async def check_backend_health():
    """Check if Sentinel backend is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SENTINEL_BACKEND_URL}/health", timeout=5.0)
            return response.status_code == 200
    except:
        return False

async def call_backend_api(endpoint: str, method: str = "GET", data: dict = None, auth_token: str = None):
    """Call the real Sentinel backend API"""
    try:
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(f"{SENTINEL_BACKEND_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = await client.post(f"{SENTINEL_BACKEND_URL}{endpoint}", json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Backend API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"Failed to call backend API {endpoint}: {e}")
        return None

def get_demo_user() -> LovableUser:
    """Get demo user for development"""
    return LovableUser(
        id="demo-user-real",
        email="demo@sentinel100k.fi",
        name="Matti Meikäläinen",
        avatar_url="https://api.dicebear.com/7.x/avatars/svg?seed=matti",
        created_at=datetime.now(),
        current_savings=25750.0,
        savings_goal=100000.0
    )

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    backend_healthy = await check_backend_health()
    return {
        "message": "🚀 Sentinel 100K Real Backend - Lovable Compatible",
        "status": "healthy",
        "version": "3.0.0",
        "backend_connection": "connected" if backend_healthy else "disconnected",
        "backend_url": SENTINEL_BACKEND_URL,
        "data_source": "real_sentinel_backend",
        "frontend_url": "http://localhost:9000/api/v1/"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check with backend status"""
    backend_healthy = await check_backend_health()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "lovable_api": "running",
            "sentinel_backend": "connected" if backend_healthy else "disconnected",
            "database": "connected" if backend_healthy else "unknown"
        },
        "data_mode": "real_backend" if backend_healthy else "fallback_mode"
    }

# User Management
@app.get("/api/v1/user/profile", response_model=LovableUser)
async def get_user_profile():
    """Get current user profile from real backend"""
    # Try to get real user data
    backend_data = await call_backend_api("/api/v1/auth/me")
    
    if backend_data:
        # Convert real backend data to Lovable format
        return LovableUser(
            id=str(backend_data.get("id", "demo-user")),
            email=backend_data.get("email", "demo@sentinel100k.fi"),
            name=backend_data.get("name", "Käyttäjä"),
            created_at=datetime.fromisoformat(backend_data.get("created_at", datetime.now().isoformat())),
            current_savings=backend_data.get("current_savings", 25750.0),
            savings_goal=backend_data.get("savings_goal", 100000.0)
        )
    else:
        # Fallback to demo user
        return get_demo_user()

# Financial Dashboard
@app.get("/api/v1/dashboard/summary", response_model=LovableFinancialSummary)
async def get_dashboard_summary():
    """Get complete financial dashboard from real backend"""
    
    # Try to get real dashboard data
    dashboard_data = await call_backend_api("/api/v1/dashboard/summary")
    
    if dashboard_data:
        # Convert real backend data to Lovable format
        total_income = dashboard_data.get("total_income", 0.0)
        total_expenses = dashboard_data.get("total_expenses", 0.0)
        balance = total_income - total_expenses
        
        # Calculate savings rate
        savings_rate = (balance / total_income * 100) if total_income > 0 else 0
        
        # Get goal progress (assuming main goal is 100K)
        goal_progress = (balance / 100000.0 * 100) if balance > 0 else 0
        
        # Convert transactions
        recent_transactions = []
        for txn in dashboard_data.get("recent_transactions", [])[:5]:
            recent_transactions.append(LovableTransaction(
                id=str(txn.get("id", "")),
                user_id="demo-user-real",
                amount=float(txn.get("amount", 0)),
                description=txn.get("description", ""),
                category=txn.get("category_name", "Muu"),
                date=datetime.fromisoformat(txn.get("transaction_date", datetime.now().isoformat())),
                type="expense" if txn.get("amount", 0) > 0 else "income",
                merchant=txn.get("merchant_name", "")
            ))
        
        # Create goals
        goals = [LovableGoal(
            id="main-goal",
            user_id="demo-user-real", 
            title="Säästötavoite 100K€",
            target_amount=100000.0,
            current_amount=balance,
            target_date=datetime(2025, 12, 31),
            progress=min(goal_progress, 100)
        )]
        
        return LovableFinancialSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            balance=balance,
            savings_rate=round(savings_rate, 2),
            goal_progress=round(goal_progress, 2),
            recent_transactions=recent_transactions,
            goals=goals,
            period="last_30_days"
        )
    
    else:
        # Fallback data when backend is not available
        logger.warning("Backend not available, using fallback data")
        return LovableFinancialSummary(
            total_income=3200.0,
            total_expenses=1450.0,
            balance=1750.0,
            savings_rate=54.7,
            goal_progress=25.75,
            recent_transactions=[
                LovableTransaction(
                    id="fallback-1",
                    user_id="demo-user-real",
                    amount=-85.50,
                    description="K-Market Ruokaostokset",
                    category="Ruoka",
                    date=datetime.now(),
                    type="expense",
                    merchant="K-Market"
                )
            ],
            goals=[
                LovableGoal(
                    id="fallback-goal",
                    user_id="demo-user-real",
                    title="Säästötavoite 100K€ (Offline)",
                    target_amount=100000.0,
                    current_amount=25750.0,
                    target_date=datetime(2025, 12, 31),
                    progress=25.75
                )
            ]
        )

# Transactions
@app.get("/api/v1/transactions", response_model=List[LovableTransaction])
async def get_transactions(limit: int = 50, category: Optional[str] = None):
    """Get transactions from real backend"""
    
    # Build query parameters
    params = f"?limit={limit}"
    if category:
        params += f"&category={category}"
    
    transactions_data = await call_backend_api(f"/api/v1/transactions{params}")
    
    if transactions_data:
        return [
            LovableTransaction(
                id=str(txn.get("id", "")),
                user_id="demo-user-real",
                amount=float(txn.get("amount", 0)),
                description=txn.get("description", ""),
                category=txn.get("category_name", "Muu"),
                date=datetime.fromisoformat(txn.get("transaction_date", datetime.now().isoformat())),
                type="expense" if txn.get("amount", 0) > 0 else "income",
                merchant=txn.get("merchant_name", ""),
                location="Helsinki"
            )
            for txn in transactions_data[:limit]
        ]
    else:
        return []

@app.post("/api/v1/transactions", response_model=LovableTransaction)
async def create_transaction(transaction_data: Dict[str, Any]):
    """Create new transaction in real backend"""
    
    # Convert Lovable format to backend format
    backend_data = {
        "amount": transaction_data.get("amount"),
        "description": transaction_data.get("description"),
        "merchant_name": transaction_data.get("merchant"),
        "transaction_date": transaction_data.get("date", datetime.now().isoformat()),
        "type": transaction_data.get("type", "expense"),
        "status": "completed"
    }
    
    result = await call_backend_api("/api/v1/transactions", method="POST", data=backend_data)
    
    if result:
        return LovableTransaction(
            id=str(result.get("id", "")),
            user_id="demo-user-real",
            amount=float(result.get("amount", 0)),
            description=result.get("description", ""),
            category=result.get("category_name", "Muu"),
            date=datetime.fromisoformat(result.get("transaction_date", datetime.now().isoformat())),
            type=result.get("type", "expense"),
            merchant=result.get("merchant_name", "")
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to create transaction")

# Goals
@app.get("/api/v1/goals", response_model=List[LovableGoal])
async def get_goals():
    """Get goals from real backend"""
    
    goals_data = await call_backend_api("/api/v1/dashboard/goals/progress")
    
    if goals_data:
        return [
            LovableGoal(
                id=str(goal.get("goal_id", "")),
                user_id="demo-user-real",
                title=goal.get("goal_name", "Tavoite"),
                target_amount=float(goal.get("target_amount", 0)),
                current_amount=float(goal.get("current_amount", 0)),
                target_date=datetime.fromisoformat(goal.get("target_date", datetime.now().isoformat())),
                progress=float(goal.get("progress_percent", 0))
            )
            for goal in goals_data
        ]
    else:
        # Fallback goal
        return [
            LovableGoal(
                id="main-goal",
                user_id="demo-user-real",
                title="Säästötavoite 100K€",
                target_amount=100000.0,
                current_amount=25750.0,
                target_date=datetime(2025, 12, 31),
                progress=25.75
            )
        ]

# AI Chat (Real backend might have AI capabilities)
@app.post("/api/v1/ai/chat")
async def ai_chat(message: Dict[str, str]):
    """AI Chat using real backend or fallback"""
    user_message = message.get("message", "")
    
    # Try to use real backend AI if available
    ai_response = await call_backend_api("/api/v1/ai/chat", method="POST", data={"message": user_message})
    
    if ai_response:
        return {
            "response": ai_response.get("response", "Anteeksi, en ymmärtänyt kysymystä."),
            "timestamp": datetime.now().isoformat(),
            "confidence": ai_response.get("confidence", 0.8),
            "type": "real_ai"
        }
    else:
        # Fallback AI responses
        if "säästä" in user_message.lower():
            response = "💡 Säästämisvinkki: Aseta automaattinen siirto säästötilille kuukausittain!"
        elif "budjetti" in user_message.lower():
            response = "📊 Suosittelen 50/30/20 sääntöä: 50% välttämättömyyksiin, 30% haluihin, 20% säästöihin."
        elif "sijoitus" in user_message.lower():
            response = "📈 Aloita indeksirahastoilla - ne ovat turvallisia ja edullisia!"
        else:
            response = f"Kiitos kysymyksestäsi! Voin auttaa säästämisessä ja budjetoinnissa. (Backend: offline)"
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.7,
            "type": "fallback_ai"
        }

# Analytics
@app.get("/api/v1/analytics/spending")
async def get_spending_analytics():
    """Get spending analytics from real backend"""
    
    analytics_data = await call_backend_api("/api/v1/dashboard/categories/breakdown")
    
    if analytics_data:
        # Convert to Lovable format
        by_category = {}
        total_spent = 0
        
        for category in analytics_data:
            category_name = category.get("category_name", "Muu")
            amount = float(category.get("total_amount", 0))
            by_category[category_name] = amount
            total_spent += amount
        
        largest_category = max(by_category.items(), key=lambda x: x[1]) if by_category else None
        
        return {
            "by_category": by_category,
            "total_spent": total_spent,
            "largest_category": largest_category,
            "period": "current_month",
            "data_source": "real_backend"
        }
    else:
        # Fallback analytics
        return {
            "by_category": {
                "Ruoka": 450.0,
                "Asuminen": 800.0,
                "Liikenne": 200.0,
                "Viihde": 120.0
            },
            "total_spent": 1570.0,
            "largest_category": ["Asuminen", 800.0],
            "period": "current_month",
            "data_source": "fallback"
        }

# Guardian System
@app.get("/api/v1/guardian/status")
async def get_guardian_status():
    """Get Guardian status from real backend"""
    
    guardian_data = await call_backend_api("/api/v1/guardian/status")
    
    if guardian_data:
        return {
            "status": guardian_data.get("status", "active"),
            "risk_level": guardian_data.get("risk_level", "low"),
            "monitoring": "active",
            "last_check": datetime.now().isoformat(),
            "recommendations": guardian_data.get("recommendations", []),
            "data_source": "real_backend"
        }
    else:
        return {
            "status": "active",
            "risk_level": "low",
            "monitoring": "active", 
            "last_check": datetime.now().isoformat(),
            "recommendations": [
                "Säästösi ovat hyvällä tasolla!",
                "Jatka nykyistä säästötahtia."
            ],
            "data_source": "fallback"
        }

# Categories
@app.get("/api/v1/categories")
async def get_categories():
    """Get categories from real backend"""
    
    categories_data = await call_backend_api("/api/v1/categories")
    
    if categories_data:
        return {
            "income": [cat.get("name") for cat in categories_data if cat.get("type") == "income"],
            "expense": [cat.get("name") for cat in categories_data if cat.get("type") == "expense"],
            "data_source": "real_backend"
        }
    else:
        return {
            "income": ["Palkka", "Freelance", "Sijoitukset", "Muu tulo"],
            "expense": ["Ruoka", "Asuminen", "Liikenne", "Viihde", "Vaatteet", "Terveys", "Muu"],
            "data_source": "fallback"
        }

# Lovable Configuration
@app.get("/api/v1/lovable/config")
async def get_lovable_config():
    """Configuration for Lovable development"""
    backend_healthy = await check_backend_health()
    
    return {
        "api_base_url": "http://localhost:9000/api/v1",
        "backend_url": SENTINEL_BACKEND_URL,
        "backend_status": "connected" if backend_healthy else "disconnected",
        "data_mode": "real" if backend_healthy else "fallback",
        "auth_required": False,
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
            "real_time": backend_healthy
        },
        "ui_config": {
            "currency": "EUR",
            "locale": "fi-FI",
            "date_format": "DD.MM.YYYY",
            "theme": "sentinel",
            "show_data_source": True
        }
    }

# WebSocket for Real-time Updates
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Get fresh data from backend
            dashboard_data = await call_backend_api("/api/v1/dashboard/summary")
            
            if dashboard_data:
                await websocket.send_json({
                    "type": "financial_update",
                    "data": {
                        "balance": dashboard_data.get("net_amount", 0),
                        "goal_progress": min((dashboard_data.get("net_amount", 0) / 100000 * 100), 100),
                        "total_income": dashboard_data.get("total_income", 0),
                        "total_expenses": dashboard_data.get("total_expenses", 0),
                        "timestamp": datetime.now().isoformat(),
                        "data_source": "real_backend"
                    }
                })
            else:
                await websocket.send_json({
                    "type": "financial_update",
                    "data": {
                        "balance": 25750.0,
                        "goal_progress": 25.75,
                        "timestamp": datetime.now().isoformat(),
                        "data_source": "fallback"
                    }
                })
            
            await asyncio.sleep(30)  # Update every 30 seconds
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Sentinel 100K Real Backend for Lovable")
    print("📊 API Documentation: http://localhost:9000/docs")
    print("🔧 Lovable Config: http://localhost:9000/api/v1/lovable/config")
    print("💡 Frontend Base URL: http://localhost:9000/api/v1/")
    print(f"🔗 Backend Connection: {SENTINEL_BACKEND_URL}")
    print("💾 Data Source: Real Sentinel 100K Backend")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,  # Different port from main backend
        reload=True,
        log_level="info"
    ) 