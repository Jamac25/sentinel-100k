#!/usr/bin/env python3
"""
Muktar's Personal Sentinel 100K Backend - Updated Version
Integrates with enhanced User model and provides real financial data.
Compatible with Lovable frontend and personal_finance_agent database.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
import json
from datetime import datetime, timedelta
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add personal_finance_agent to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'personal_finance_agent'))

try:
    from app.models import User, AgentState, Goal, Transaction
    from app.core.config import settings
    from app.db.base import Base
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Database models not available: {e}")
    DATABASE_AVAILABLE = False

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Muktar's Sentinel 100K Backend",
    description="Personal finance backend for Muktar with real data integration",
    version="2.0.0"
)

# CORS for Lovable integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://lovable.dev",
        "https://*.lovable.dev",
        "http://localhost:9000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
if DATABASE_AVAILABLE:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Pydantic models
class UserProfile(BaseModel):
    name: str
    current_savings: float
    monthly_income: float
    savings_goal: float
    savings_rate: float
    months_to_goal: Optional[int]
    family_support: float
    workplace: str
    profession: str

class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    goal_progress: float

class ChatMessage(BaseModel):
    message: str
    timestamp: str
    sender: str

# Real data access functions
def get_muktar_profile(db: Session = None) -> Dict[str, Any]:
    """Get Muktar's profile from database or return default."""
    
    if DATABASE_AVAILABLE and db:
        try:
            muktar = db.query(User).filter(User.username == "muktar").first()
            if muktar:
                return {
                    "name": muktar.full_name or "Muktar",
                    "current_savings": muktar.current_savings or 220.0,
                    "monthly_income": muktar.monthly_income or 4700.0,
                    "savings_goal": muktar.savings_goal or 100000.0,
                    "savings_rate": muktar.savings_rate_percentage,
                    "months_to_goal": int(muktar.months_to_goal) if muktar.months_to_goal else 61,
                    "family_support": muktar.family_support or 500.0,
                    "workplace": muktar.workplace or "Terveystalo + Own Business",
                    "profession": muktar.profession or "Healthcare Professional & Entrepreneur",
                    "primary_job_income": muktar.primary_job_income or 3200.0,
                    "business_income": muktar.business_income or 1500.0,
                    "housing_costs": muktar.housing_costs or 1720.0,
                    "food_costs": muktar.food_costs or 500.0,
                    "transport_costs": muktar.transport_costs or 200.0,
                    "entertainment_costs": muktar.entertainment_costs or 150.0,
                    "family_info": muktar.family_info,
                    "total_expenses": muktar.total_monthly_expenses
                }
        except Exception as e:
            logger.error(f"Error getting Muktar's profile: {e}")
    
    # Fallback to known data
    return {
        "name": "Muktar",
        "current_savings": 220.0,
        "monthly_income": 4700.0,
        "savings_goal": 100000.0,
        "savings_rate": 34.7,
        "months_to_goal": 61,
        "family_support": 500.0,
        "workplace": "Terveystalo + Oma yritys",
        "profession": "Terveydenhuollon ammattilainen & Yrittäjä",
        "primary_job_income": 3200.0,
        "business_income": 1500.0,
        "housing_costs": 1720.0,
        "food_costs": 500.0,
        "transport_costs": 200.0,
        "entertainment_costs": 150.0,
        "family_info": "Tukee lapsia Somaliassa 500€/kk",
        "total_expenses": 3070.0
    }

def get_transactions_data(db: Session = None) -> List[Dict[str, Any]]:
    """Get Muktar's transactions from database or return sample data."""
    
    if DATABASE_AVAILABLE and db:
        try:
            muktar = db.query(User).filter(User.username == "muktar").first()
            if muktar:
                transactions = db.query(Transaction).filter(Transaction.user_id == muktar.id).limit(10).all()
                return [
                    {
                        "id": t.id,
                        "description": t.description,
                        "amount": t.amount,
                        "date": t.transaction_date.isoformat() if t.transaction_date else datetime.now().isoformat(),
                        "category": "Unknown",  # TODO: Add category relationship
                        "type": "income" if t.amount > 0 else "expense"
                    }
                    for t in transactions
                ]
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
    
    # Sample transactions based on Muktar's profile
    return [
        {"id": 1, "description": "Terveystalo palkka", "amount": 3200, "date": "2024-12-01", "category": "Palkka", "type": "income"},
        {"id": 2, "description": "Oma yritys tulot", "amount": 1500, "date": "2024-12-01", "category": "Yritystoiminta", "type": "income"},
        {"id": 3, "description": "Vuokra", "amount": -1500, "date": "2024-12-01", "category": "Asuminen", "type": "expense"},
        {"id": 4, "description": "Sähkö ja vesi", "amount": -220, "date": "2024-12-01", "category": "Asuminen", "type": "expense"},
        {"id": 5, "description": "Ruokaostokset", "amount": -500, "date": "2024-12-05", "category": "Ruoka", "type": "expense"},
        {"id": 6, "description": "HSL-kuukausilippu", "amount": -200, "date": "2024-12-01", "category": "Kuljetus", "type": "expense"},
        {"id": 7, "description": "Tuki lapsille Somaliassa", "amount": -500, "date": "2024-12-01", "category": "Perheen tuki", "type": "expense"},
        {"id": 8, "description": "Vaatteet ja vapaa-aika", "amount": -150, "date": "2024-12-10", "category": "Vapaa-aika", "type": "expense"}
    ]

# AI Chat with personalized responses
def get_ai_response(message: str, profile: Dict[str, Any]) -> str:
    """Generate personalized AI response for Muktar."""
    
    message_lower = message.lower()
    name = profile.get("name", "Muktar")
    savings_rate = profile.get("savings_rate", 34.7)
    family_support = profile.get("family_support", 500)
    months_to_goal = profile.get("months_to_goal", 61)
    
    if any(word in message_lower for word in ["hei", "moi", "terve", "hello"]):
        return f"Hei {name}! 👋 Mukava nähdä sinut taas. Säästöprosenttisi {savings_rate:.1f}% on edelleen erinomainen! Miten voin auttaa sinua tänään?"
    
    elif any(word in message_lower for word in ["säästöt", "savings", "raha"]):
        return f"Hienoa, {name}! 💰 Tällä hetkellä säästät €{profile.get('current_savings', 220):.0f} ja säästöprosenttisi {savings_rate:.1f}% on todella hyvä. Saavutat 100k€ tavoitteen noin {months_to_goal} kuukaudessa!"
    
    elif any(word in message_lower for word in ["somalia", "lapset", "perhe", "tuki"]):
        return f"Se on ihmeellistä, {name}! 🌍❤️ Tuet lapsiasi Somaliassa {family_support}€/kk - se osoittaa suurta vastuuntuntoa. Pystyt silti säästämään erinomaisen hyvin ja saavuttamaan tavoitteesi."
    
    elif any(word in message_lower for word in ["työ", "terveystalo", "yritys"]):
        return f"Hienoa, {name}! 💼 Työskentelet Terveystalossa (€3200/kk) ja sinulla on oma yritys (€1500/kk). Tämä kaksoistulovirta antaa sinulle vahvan taloudellisen perustan!"
    
    elif any(word in message_lower for word in ["budjetti", "menot", "kulut"]):
        housing = profile.get("housing_costs", 1720)
        food = profile.get("food_costs", 500)
        transport = profile.get("transport_costs", 200)
        return f"Kuukausimenoistasi {name}: Asuminen €{housing:.0f}, Ruoka €{food:.0f}, Liikenne €{transport:.0f}, Perheen tuki €{family_support:.0f}. Yhteensä €{profile.get('total_expenses', 3070):.0f}. Hallitset menojasi hyvin!"
    
    elif any(word in message_lower for word in ["tavoite", "100k", "goal"]):
        goal_amount = profile.get("savings_goal", 100000)
        current = profile.get("current_savings", 220)
        remaining = goal_amount - current
        return f"Tavoitteesi €{goal_amount:,.0f}! 🎯 Sinulla on €{current:.0f} ja tarvitset vielä €{remaining:,.0f}. Nykyisellä säästöprosenttiksi {savings_rate:.1f}% saavutat sen {months_to_goal} kuukaudessa. Olet oikealla tiellä!"
    
    elif any(word in message_lower for word in ["vinkkejä", "neuvoja", "tips", "advice"]):
        return f"Neuvoja sinulle {name}: 1) Säästöprosenttisi {savings_rate:.1f}% on jo erinomainen! 2) Harkitse yritystulojesi kasvattamista 3) Perheen tukeminen on tärkeää - se on osa vastuullista elämää 4) Jatka samaan malliin, olet menestyksekäs! 🌟"
    
    elif any(word in message_lower for word in ["kiitos", "thank", "hyva"]):
        return f"Ole hyvä {name}! 😊 Olen aina täällä tukemassa taloudellista matkaasi. Muista: olet jo nyt erittäin hyvässä tilanteessa säästöprosentillasi {savings_rate:.1f}%!"
    
    else:
        return f"Hei {name}! 🤖 Olen Sentinel, henkilökohtainen talousassistenttisi. Voin auttaa säästöjen, budjetin ja tavoitteiden kanssa. Säästöprosenttisi {savings_rate:.1f}% on loistava ja perheen tukeminen Somaliassa on kunnioitettavaa! Mitä haluaisit tietää?"

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Muktar's Sentinel 100K Backend v2.0 - Real Data Integration", "status": "active"}

@app.get("/api/user/profile")
async def get_user_profile(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get Muktar's complete profile."""
    profile = get_muktar_profile(db)
    return {
        "user": {
            "name": profile["name"],
            "current_savings": profile["current_savings"],
            "monthly_income": profile["monthly_income"],
            "savings_goal": profile["savings_goal"],
            "savings_rate": profile["savings_rate"],
            "months_to_goal": profile["months_to_goal"],
            "family_support": profile["family_support"],
            "workplace": profile["workplace"],
            "profession": profile["profession"]
        }
    }

@app.get("/api/dashboard")
async def get_dashboard(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get dashboard data for Muktar."""
    profile = get_muktar_profile(db)
    
    return {
        "summary": {
            "current_savings": profile["current_savings"],
            "monthly_income": profile["monthly_income"],
            "monthly_expenses": profile["total_expenses"],
            "net_savings": profile["monthly_income"] - profile["total_expenses"],
            "savings_rate": profile["savings_rate"],
            "goal_progress": (profile["current_savings"] / profile["savings_goal"]) * 100
        },
        "breakdown": {
            "income": [
                {"source": "Terveystalo", "amount": profile["primary_job_income"]},
                {"source": "Oma yritys", "amount": profile["business_income"]}
            ],
            "expenses": [
                {"category": "Asuminen", "amount": profile["housing_costs"]},
                {"category": "Ruoka", "amount": profile["food_costs"]},
                {"category": "Liikenne", "amount": profile["transport_costs"]},
                {"category": "Vapaa-aika", "amount": profile["entertainment_costs"]},
                {"category": "Perheen tuki (Somalia)", "amount": profile["family_support"]}
            ]
        },
        "goals": {
            "primary_goal": {
                "title": "€100,000 säästöt",
                "current": profile["current_savings"],
                "target": profile["savings_goal"],
                "progress": (profile["current_savings"] / profile["savings_goal"]) * 100,
                "months_remaining": profile["months_to_goal"]
            }
        },
        "achievements": [
            {"title": "Erinomainen säästöprosentti", "description": f"{profile['savings_rate']:.1f}% - Paljon keskiarvon yläpuolella!"},
            {"title": "Kaksoistulovirta", "description": "Terveystalo + oma yritys"},
            {"title": "Vastuullinen perheenisä", "description": "Tukee lapsia Somaliassa"},
            {"title": "Tavoitteellinen säästäjä", "description": "Selkeä 100k€ tavoite"}
        ]
    }

@app.get("/api/transactions")
async def get_transactions(limit: int = 20, db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get Muktar's transactions."""
    transactions = get_transactions_data(db)
    return {
        "transactions": transactions[:limit],
        "total": len(transactions)
    }

@app.post("/api/chat")
async def chat_with_ai(message: ChatMessage, db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Chat with AI assistant using Muktar's profile."""
    profile = get_muktar_profile(db)
    response = get_ai_response(message.message, profile)
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "context": {
            "user": profile["name"],
            "savings_rate": profile["savings_rate"],
            "family_support": profile["family_support"]
        }
    }

@app.get("/api/financial-summary")
async def get_financial_summary(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get Muktar's financial summary."""
    profile = get_muktar_profile(db)
    
    return {
        "summary": {
            "total_income": profile["monthly_income"],
            "total_expenses": profile["total_expenses"],
            "net_savings": profile["monthly_income"] - profile["total_expenses"],
            "savings_rate": profile["savings_rate"],
            "goal_progress": (profile["current_savings"] / profile["savings_goal"]) * 100,
            "months_to_goal": profile["months_to_goal"]
        },
        "insights": [
            f"Säästöprosenttisi {profile['savings_rate']:.1f}% on erinomainen!",
            f"Saavutat 100k€ tavoitteen {profile['months_to_goal']} kuukaudessa",
            f"Tuet perhettä Somaliassa {profile['family_support']}€/kk - vastuullista!",
            "Kaksoistulovirta antaa hyvän turvan"
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """WebSocket connection for real-time updates."""
    await manager.connect(websocket)
    profile = get_muktar_profile(db)
    
    # Send welcome message
    await manager.send_personal_message(
        json.dumps({
            "type": "welcome",
            "message": f"Tervetuloa takaisin, {profile['name']}! Säästöprosenttisi {profile['savings_rate']:.1f}% näyttää hyvältä!",
            "data": profile
        }),
        websocket
    )
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat":
                response = get_ai_response(message_data.get("message", ""), profile)
                await manager.send_personal_message(
                    json.dumps({
                        "type": "chat_response",
                        "message": response,
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Muktar's Sentinel 100K Backend",
        "version": "2.0.0",
        "database": "connected" if DATABASE_AVAILABLE else "fallback_mode",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Muktar's Personal Sentinel 100K Backend v2.0")
    print("=" * 60)
    print("💰 Real data integration enabled")
    print("🌍 Family support to Somalia recognized")
    print("💼 Dual income (Terveystalo + Business) tracked")
    print("📊 34.7% savings rate - EXCELLENT!")
    print("🎯 61 months to €100,000 goal")
    print("=" * 60)
    print("📍 Backend: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws")
    print("🎨 Compatible with Lovable frontend")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # Disable reload to prevent scheduler issues
    ) 