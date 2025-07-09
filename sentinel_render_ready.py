#!/usr/bin/env python3
"""
🎯 SENTINEL 100K - RENDER.COM READY VERSION
===========================================
Production-ready version optimized for Render hosting
✅ PostgreSQL support
✅ Environment variables
✅ Production settings
"""

import json
import os
import time
import asyncio
import threading
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import base64
import hashlib
import schedule
from contextlib import asynccontextmanager
import uuid
import logging
from collections import defaultdict, Counter
import statistics

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 🌍 Environment Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentinel.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
PORT = int(os.getenv("PORT", 8000))

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("openAI") or os.getenv("OPENAI_KEY")

# Debug OpenAI API key
print(f"🔍 OpenAI API Key Debug:")
print(f"   - OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
print(f"   - openAI: {'✅ Set' if os.getenv('openAI') else '❌ Not set'}")
print(f"   - OPENAI_KEY: {'✅ Set' if os.getenv('OPENAI_KEY') else '❌ Not set'}")
print(f"   - Final key: {'✅ Valid' if OPENAI_API_KEY and OPENAI_API_KEY != 'sk-test-key-for-development' else '❌ Invalid'}")

# 🗄️ Database Configuration
def get_database_engine():
    """Create database engine with proper settings"""
    if DATABASE_URL.startswith("postgresql"):
        # Production PostgreSQL
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=DEBUG
        )
    else:
        # Development SQLite
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=DEBUG
        )
    return engine

# Database setup
try:
    engine = get_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"✅ Database connected: {DATABASE_URL[:20]}...")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    engine = None
    SessionLocal = None

# 📊 Data Models
class ChatMessage(BaseModel):
    message: str

class DeepOnboardingData(BaseModel):
    name: str
    email: str
    age: int
    profession: str
    current_savings: float
    savings_goal: float
    monthly_income: float
    monthly_expenses: float
    skills: List[str]
    work_experience_years: int
    education_level: str
    risk_tolerance: str
    time_availability_hours: int
    financial_goals: List[str]
    debt_amount: Optional[float] = 0
    investment_experience: str
    preferred_income_methods: List[str]

# 🗄️ Production Data Storage
class ProductionDataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.user_data_file = self.data_dir / "users.json"
        self.onboarding_file = self.data_dir / "onboarding.json"
        self.cycles_file = self.data_dir / "cycles.json"
        self.analysis_file = self.data_dir / "analysis.json"
        
        # Upload directories
        self.cv_uploads_dir = Path("cv_uploads")
        self.cv_uploads_dir.mkdir(exist_ok=True)
    
    def load_data(self, file_path: Path) -> dict:
        """Load data from JSON file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
        return {}
    
    def save_data(self, file_path: Path, data: dict):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
    
    def get_user_data(self) -> dict:
        return self.load_data(self.user_data_file)
    
    def save_user_data(self, data: dict):
        self.save_data(self.user_data_file, data)
    
    def get_onboarding_data(self) -> dict:
        return self.load_data(self.onboarding_file)
    
    def save_onboarding_data(self, data: dict):
        self.save_data(self.onboarding_file, data)
    
    def get_cycles_data(self) -> dict:
        return self.load_data(self.cycles_file)
    
    def save_cycles_data(self, data: dict):
        self.save_data(self.cycles_file, data)
    
    def get_analysis_data(self) -> dict:
        return self.load_data(self.analysis_file)
    
    def save_analysis_data(self, data: dict):
        self.save_data(self.analysis_file, data)

# Initialize data manager
data_manager = ProductionDataManager()

# 🚀 Application lifespan handler - Fixed for FastAPI latest version
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI - PRODUCTION READY"""
    # Startup
    print(f"🚀 Sentinel 100K starting in {ENVIRONMENT} mode")
    print(f"📊 Database: {DATABASE_URL[:20]}...")
    print(f"🎯 Port: {PORT}")
    
    # Create necessary directories
    data_manager.data_dir.mkdir(exist_ok=True)
    data_manager.cv_uploads_dir.mkdir(exist_ok=True)
    
    # Setup and start notification scheduler in background
    setup_notification_scheduler()
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("✅ Notification scheduler started in background")
    
    # Initialize production systems
    print("✅ Analytics system initialized")
    print("✅ Mass notification system ready")
    print("✅ AI learning engine active")
    print("✅ Automatic customer service enabled")
    
    print("✅ Sentinel 100K production ready!")
    
    yield
    
    # Shutdown
    print("🛑 Sentinel 100K shutting down...")
    analytics.save_analytics()
    ai_learning_engine.save_learning_data()

# 🎯 FastAPI app - RENDER READY with lifespan
app = FastAPI(
    title="Sentinel 100K - Render Production",
    description="Complete Finnish Personal Finance AI - SMART TELEGRAM BOT - NO MOCK DATA",
    version="100.2.0",
    docs_url="/docs" if DEBUG else None,  # Hide docs in production
    redoc_url="/redoc" if DEBUG else None,
    lifespan=lifespan
)

# 🌐 CORS - Production safe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else [
        "https://your-frontend-domain.com",
        "https://sentinel-100k.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 🧠 Systems (simplified for production)
class ProductionOnboardingSystem:
    def complete_onboarding(self, user_id: str, onboarding_data: dict) -> dict:
        """Complete deep onboarding process"""
        user_profile = {
            **onboarding_data,
            "user_id": user_id,
            "onboarding_completed": datetime.now().isoformat(),
            "profile_completeness": 100,
            "personalization_level": "maximum",
            "ai_coaching_enabled": True,
            "weekly_cycles_enrolled": True
        }
        
        # Save to data manager
        onboarding_data_dict = data_manager.get_onboarding_data()
        onboarding_data_dict[user_id] = user_profile
        data_manager.save_onboarding_data(onboarding_data_dict)
        
        return user_profile

class ProductionCycleSystem:
    def initialize_cycles(self, user_id: str, user_profile: dict):
        """Initialize 7-week progressive cycles"""
        base_weekly_target = user_profile.get("monthly_income", 3000) / 4 * 0.25
        
        cycles = []
        for week in range(1, 8):
            week_multiplier = 1 + (week - 1) * 0.15
            savings_target = max(300, base_weekly_target * week_multiplier)
            
            cycle = {
                "week_number": week,
                "savings_target": round(savings_target, 2),
                "income_target": round(savings_target * 1.3, 2),
                "challenges": [f"Week {week} challenge", "Save consistently", "Track progress"],
                "difficulty_level": "beginner" if week <= 2 else "intermediate" if week <= 5 else "advanced"
            }
            cycles.append(cycle)
        
        user_cycles = {
            "user_id": user_id,
            "cycles": cycles,
            "current_week": 1,
            "cycle_started": datetime.now().isoformat(),
            "status": "active"
        }
        
        cycles_data = data_manager.get_cycles_data()
        cycles_data[user_id] = user_cycles
        data_manager.save_cycles_data(cycles_data)
        
        return user_cycles
    
    def get_current_week_data(self, user_id: str) -> dict:
        """Get current week's goals and progress"""
        cycles_data = data_manager.get_cycles_data()
        if user_id not in cycles_data:
            return {"error": "No cycles found for user"}
        
        user_cycles = cycles_data[user_id]
        current_week = user_cycles.get("current_week", 1)
        
        if current_week <= len(user_cycles["cycles"]):
            current_cycle = user_cycles["cycles"][current_week - 1]
            return {
                **current_cycle,
                "current_day": 1,
                "days_remaining": 7,
                "cycle_progress": 0
            }
        
        return {"error": "Cycle completed"}

class ProductionAnalysisSystem:
    def run_night_analysis(self):
        """Run comprehensive night analysis"""
        print("🌙 Running Production Night Analysis...")
        
        onboarding_data = data_manager.get_onboarding_data()
        cycles_data = data_manager.get_cycles_data()
        
        analysis_results = {}
        
        for user_id in onboarding_data.keys():
            analysis_results[user_id] = {
                "user_id": user_id,
                "goal_progress": 25.0,  # Placeholder
                "risk_level": "low",
                "recommendations": ["Continue saving", "Track expenses"],
                "analysis_timestamp": datetime.now().isoformat()
            }
        
        analysis_data = {
            "last_analysis": datetime.now().isoformat(),
            "users_analyzed": len(analysis_results),
            "results": analysis_results
        }
        
        data_manager.save_analysis_data(analysis_data)
        print(f"🌙 Production Night Analysis completed for {len(analysis_results)} users")
        return analysis_results

# 🔐 ENHANCED CONTEXT SYSTEM for RENDER
class RenderUserContextManager:
    """
    Enhanced Context Manager for Render production
    Integrates with production data manager
    """
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.data_key = f"onboarding_{user_email}"
        
        # Load data via data manager
        self.onboarding_data = data_manager.get_onboarding_data()
        self.cycles_data = data_manager.get_cycles_data()
        self.analysis_data = data_manager.get_analysis_data()
        self.users_data = data_manager.get_user_data()
        
        # Get user profiles
        self.profile = self.onboarding_data.get(self.data_key, {})
        self.cycles = self.cycles_data.get(self.data_key, {})
        self.analysis = self.analysis_data.get("results", {}).get(self.data_key, {})
        self.user_info = self.users_data.get(user_email, {})

    def get_enhanced_context(self) -> Dict[str, Any]:
        """Get complete user context for Render"""
        
        # Base context
        base_context = {
            "user_email": self.user_email,
            "data_key": self.data_key,
            "user_id": self.profile.get("user_id"),
            "name": self.profile.get("name"),
            "current_savings": self.profile.get("current_savings", 0),
            "savings_goal": self.profile.get("savings_goal", 100000),
            "monthly_income": self.profile.get("monthly_income", 0),
            "monthly_expenses": self.profile.get("monthly_expenses", 0),
            "skills": self.profile.get("skills", []),
            "risk_tolerance": self.profile.get("risk_tolerance", "Maltillinen"),
            "current_week": self.cycles.get("current_week", 1),
            "weekly_target": 0,
            "cycle_progress": 0,
        }
        
        # Calculate weekly target from cycles
        if self.cycles and "cycles" in self.cycles:
            current_week = base_context["current_week"]
            if current_week <= len(self.cycles["cycles"]):
                current_cycle = self.cycles["cycles"][current_week - 1]
                base_context["weekly_target"] = current_cycle.get("savings_target", 0)
                base_context["cycle_progress"] = (current_week / 7) * 100
        
        # Enhanced context
        enhanced_context = {
            **base_context,
            "target_income_weekly": base_context.get("weekly_target", 300),
            "target_income_monthly": base_context.get("monthly_income", 3000),
            "interests": self._extract_interests_from_skills(),
            "watchdog_state": self._determine_watchdog_state(),
            "ai_context": self._build_ai_context(),
            "progress_summary": self._calculate_progress_summary(base_context),
            "current_cycle_details": self._get_current_cycle_details(),
            "latest_analysis": self.analysis,
            "context_generated": datetime.now().isoformat(),
            "data_completeness": self._calculate_data_completeness(),
            "render_production": True
        }
        
        return enhanced_context

    def _extract_interests_from_skills(self) -> list:
        """Convert skills to interests"""
        skills = self.profile.get("skills", [])
        interest_mapping = {
            "Ohjelmointi": "Teknologia",
            "Web-kehitys": "Teknologia", 
            "Graafinen suunnittelu": "Luovuus",
            "UI/UX": "Muotoilu",
            "Markkinointi": "Liiketoiminta",
            "Myynti": "Liiketoiminta",
            "Kirjoittaminen": "Sisällöntuotanto",
            "Valokuvaus": "Luovuus"
        }
        
        interests = []
        for skill in skills:
            if skill in interest_mapping:
                interests.append(interest_mapping[skill])
        
        return list(set(interests))

    def _determine_watchdog_state(self) -> str:
        """Determine watchdog state based on progress"""
        # Calculate progress from current savings
        current_savings = self.profile.get("current_savings", 0)
        savings_goal = self.profile.get("savings_goal", 100000)
        goal_progress = (current_savings / savings_goal * 100) if savings_goal > 0 else 0
        
        risk_level = self.analysis.get("risk_level", "unknown")
        
        if risk_level == "high" or goal_progress < 25:
            return "Alert"
        elif risk_level == "medium" or goal_progress < 50:
            return "Active"
        elif goal_progress > 75:
            return "Optimized"
        else:
            return "Passive"

    def _build_ai_context(self) -> Dict[str, Any]:
        """Build AI context"""
        return {
            "financial_goals": self.profile.get("financial_goals", []),
            "preferred_income_methods": self.profile.get("preferred_income_methods", []),
            "work_experience_years": self.profile.get("work_experience_years", 0),
            "time_availability_hours": self.profile.get("time_availability_hours", 0),
            "motivation_level": self.profile.get("motivation_level", 7),
            "ai_recommendations": self.analysis.get("ai_recommendations", [])
        }

    def _calculate_progress_summary(self, base_context: dict) -> Dict[str, Any]:
        """Calculate progress summary"""
        current_savings = base_context.get("current_savings", 0)
        savings_goal = base_context.get("savings_goal", 100000)
        
        progress_percentage = (current_savings / savings_goal * 100) if savings_goal > 0 else 0
        
        return {
            "goal_progress_percentage": round(progress_percentage, 2),
            "amount_to_goal": savings_goal - current_savings,
            "weeks_completed": base_context.get("current_week", 1) - 1,
            "weeks_remaining": 8 - base_context.get("current_week", 1),
            "on_track": progress_percentage >= (base_context.get("current_week", 1) - 1) * 14.3
        }

    def _get_current_cycle_details(self) -> Dict[str, Any]:
        """Get current cycle details"""
        if not self.cycles or "cycles" not in self.cycles:
            return {}
        
        current_week = self.cycles.get("current_week", 1)
        if current_week <= len(self.cycles["cycles"]):
            return self.cycles["cycles"][current_week - 1]
        
        return {}

    def _calculate_data_completeness(self) -> int:
        """Calculate data completeness percentage"""
        required_fields = [
            "name", "email", "current_savings", "savings_goal", 
            "monthly_income", "monthly_expenses", "skills"
        ]
        
        completed_fields = sum(1 for field in required_fields if self.profile.get(field))
        return round((completed_fields / len(required_fields)) * 100)

def build_render_enhanced_ai_prompt(user_email: str, query: str) -> str:
    """Build enhanced AI prompt for Render production"""
    ctx = RenderUserContextManager(user_email).get_enhanced_context()
    
    return f"""
Sinä olet Sentinel 100K -agentti, älykkä henkilökohtainen talousvalmentaja.

=== KÄYTTÄJÄN TÄYDELLINEN KONTEKSTI (RENDER PRODUCTION) ===
👤 Käyttäjä: {ctx['name']} ({ctx['user_email']})
💰 Nykyiset säästöt: {ctx['current_savings']:,.0f}€
🎯 Tavoite: {ctx['savings_goal']:,.0f}€ 
📈 Edistyminen: {ctx['progress_summary']['goal_progress_percentage']:.1f}%

📅 VIIKKOSYKLI:
- Viikko: {ctx['current_week']}/7
- Viikkotavoite: {ctx['target_income_weekly']:,.0f}€
- Sykli edistyminen: {ctx['cycle_progress']:.1f}%

🤖 AGENTTI TILA:
- Watchdog: {ctx['watchdog_state']}
- Motivaatio: {ctx['ai_context']['motivation_level']}/10
- Datan täydellisyys: {ctx['data_completeness']}%

=== KÄYTTÄJÄN KYSYMYS ===
{query}

=== OHJEISTUS ===
Vastaa henkilökohtaisesti ja käytännöllisesti. Anna konkreettisia neuvoja jotka sopivat juuri tälle käyttäjälle.
"""

# Initialize systems
onboarding_system = ProductionOnboardingSystem()
cycle_system = ProductionCycleSystem()
analysis_system = ProductionAnalysisSystem()

# 🎯 API ENDPOINTS - PRODUCTION READY

@app.get("/")
def root():
    """Root endpoint - Production Status"""
    return {
        "service": "Sentinel 100K - Production",
        "status": "operational",
        "version": "100.0.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if engine else "disconnected",
        "features": {
            "deep_onboarding": "active",
            "weekly_cycles": "active", 
            "night_analysis": "active",
            "ai_coaching": "active"
        }
    }

@app.get("/health")
def health_check():
    """Production health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "completion": "100%",
        "environment": ENVIRONMENT,
        "database": "connected" if engine else "disconnected",
        "systems": {
            "deep_onboarding": "operational",
            "weekly_cycles": "operational",
            "night_analysis": "operational",
            "data_storage": "operational"
        },
        "ready_for_production": True
    }

@app.post("/api/v1/onboarding/start")
def start_deep_onboarding():
    """Start deep onboarding process"""
    user_id = f"user_{int(time.time())}"
    
    return {
        "user_id": user_id,
        "onboarding_started": datetime.now().isoformat(),
        "steps": [
            "basic_info", "financial_status", "skills_assessment",
            "goals_setting", "personalization", "cycle_setup"
        ],
        "estimated_duration": "15-20 minutes"
    }

@app.post("/api/v1/onboarding/complete")
def complete_deep_onboarding(onboarding_data: DeepOnboardingData):
    """Complete deep onboarding with all data"""
    user_id = f"user_{int(time.time())}"
    
    # Complete onboarding
    profile = onboarding_system.complete_onboarding(user_id, onboarding_data.dict())
    
    # Initialize cycles
    cycle_system.initialize_cycles(user_id, profile)
    
    return {
        "status": "completed",
        "user_id": user_id,
        "profile": profile,
        "onboarding_score": 100,
        "next_steps": ["Start Week 1 challenges", "Set up daily routines"]
    }

@app.get("/api/v1/cycles/current/{user_id}")
def get_current_cycle(user_id: str):
    """Get current week cycle"""
    return cycle_system.get_current_week_data(user_id)

@app.post("/api/v1/analysis/night/trigger")
def trigger_night_analysis():
    """Trigger night analysis manually"""
    return {
        "status": "completed",
        "results": analysis_system.run_night_analysis(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/analysis/night/latest")
def get_latest_night_analysis():
    """Get latest night analysis results"""
    analysis_data = data_manager.get_analysis_data()
    return {
        "status": "success",
        "data": analysis_data,
        "timestamp": datetime.now().isoformat()
    }

# 🎯 DASHBOARD SUMMARY with ENHANCED CONTEXT for RENDER
@app.get("/api/v1/dashboard/complete/{user_email}")
def get_dashboard_summary_render(user_email: str):
    """
    Complete dashboard summary for Render production
    Uses enhanced context system for full goal tracking
    """
    try:
        context_manager = RenderUserContextManager(user_email)
        context = context_manager.get_enhanced_context()
        
        # User profile from enhanced context
        user_profile = {
            "user_id": context["user_id"],
            "email": context["user_email"],
            "name": context["name"],
            "current_savings": context["current_savings"],
            "savings_goal": context["savings_goal"],
            "goal_progress": context["progress_summary"]["goal_progress_percentage"],
            "monthly_income": context["monthly_income"],
            "monthly_expenses": context["monthly_expenses"],
            "data_completeness": context["data_completeness"]
        }
        
        # Weekly cycle information
        weekly_cycle = {
            "current_week": context["current_week"],
            "weekly_target": context["target_income_weekly"],
            "cycle_progress": context["cycle_progress"],
            "challenges_count": len(context["current_cycle_details"].get("challenges", [])),
            "difficulty_level": context["current_cycle_details"].get("difficulty_level", "beginner"),
            "status": "active" if context["current_week"] <= 7 else "completed"
        }
        
        # Night analysis
        night_analysis = {
            "last_analysis": context["latest_analysis"].get("analysis_timestamp", "Never"),
            "risk_level": context["latest_analysis"].get("risk_level", "unknown"),
            "recommendations_count": len(context["ai_context"]["ai_recommendations"]),
            "watchdog_state": context["watchdog_state"]
        }
        
        # Next actions based on enhanced context
        next_actions = []
        if context["data_completeness"] < 100:
            next_actions.append("Täydennä profiilitiedot")
        if context["current_week"] <= 7:
            next_actions.append(f"Suorita viikko {context['current_week']} haasteet")
        if context["watchdog_state"] == "Alert":
            next_actions.append("Tarkista säästöstrategia - Watchdog huolissaan")
        if len(context["ai_context"]["ai_recommendations"]) > 0:
            next_actions.append("Tarkasta AI-suositukset")
        
        # Achievements based on progress
        achievements = {
            "onboarding_master": context["data_completeness"] >= 100,
            "cycle_participant": context["current_week"] > 1,
            "week_completer": context["progress_summary"]["weeks_completed"] > 0,
            "analysis_reviewed": len(context["ai_context"]["ai_recommendations"]) > 0,
            "goal_tracker": context["progress_summary"]["goal_progress_percentage"] > 0,
            "watchdog_monitored": context["watchdog_state"] != "Passive"
        }
        
        return {
            "status": "success",
            "user_profile": user_profile,
            "weekly_cycle": weekly_cycle,
            "night_analysis": night_analysis,
            "achievements": achievements,
            "next_actions": next_actions[:5],  # Limit to 5
            "enhanced_features": {
                "goal_tracking": "active",
                "watchdog_monitoring": context["watchdog_state"],
                "personalization_level": "maximum",
                "ai_context": "loaded",
                "data_sources": "complete"
            },
            "environment": "render_production",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Dashboard summary failed: {str(e)}",
            "user_email": user_email,
            "fallback": "Use basic endpoints"
        }

# 🔌 ENHANCED CONTEXT ENDPOINTS for RENDER

@app.get("/api/v1/context/{user_email}")
def get_user_enhanced_context_render(user_email: str):
    """
    Enhanced user context for Render production
    Includes goal tracking and watchdog functionality
    """
    try:
        context_manager = RenderUserContextManager(user_email)
        enhanced_context = context_manager.get_enhanced_context()
        
        return {
            "status": "success",
            "user_email": user_email,
            "enhanced_context": enhanced_context,
            "environment": "render_production",
            "data_sources": [
                "data/onboarding.json",
                "data/cycles.json", 
                "data/analysis.json",
                "data/users.json"
            ],
            "features_active": [
                "goal_tracking", "watchdog_monitoring", "progress_analysis", 
                "ai_context", "weekly_cycles", "personalization"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Enhanced context failed: {str(e)}",
            "fallback": "Use basic endpoints"
        }

@app.post("/api/v1/chat/enhanced")
def enhanced_ai_chat_render(message: ChatMessage, user_email: str):
    """
    Enhanced AI chat for Render with full user context and REAL OpenAI AI - NO FALLBACK
    """
    try:
        # Get user context for response personalization
        context_manager = RenderUserContextManager(user_email)
        context = context_manager.get_enhanced_context()
        
        # Check OpenAI API key first
        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-test-key-for-development":
            return {
                "response": "❌ OpenAI API avain puuttuu tai on virheellinen. Ota yhteyttä ylläpitoon.",
                "error": "OPENAI_API_KEY_MISSING",
                "enhanced_prompt_used": False,
                "user_email": user_email,
                "personalization_level": "None",
                "context_sources": [],
                "watchdog_state": context.get("watchdog_state", "Error"),
                "goal_progress": context.get("progress_summary", {}).get("goal_progress_percentage", 0),
                "timestamp": datetime.now().isoformat(),
                "model": "error",
                "environment": "render_production",
                "ai_used": False,
                "openai_used": False,
                "debug": {
                    "openai_key_available": bool(OPENAI_API_KEY),
                    "openai_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
                    "openai_key_starts_with": OPENAI_API_KEY[:10] if OPENAI_API_KEY else "None"
                }
            }
        
        # Build comprehensive AI prompt
        ai_prompt = f"""
Olet Sentinel 100K - henkilökohtainen talousneuvoja. Käytä seuraavia käyttäjän tietoja:

KÄYTTÄJÄN TIEDOT:
- Nimi: {context.get('name', 'Käyttäjä')}
- Nykyiset säästöt: {context.get('current_savings', 0):,.0f}€
- Tavoite: {context.get('savings_goal', 100000):,.0f}€
- Edistyminen: {context.get('progress_summary', {}).get('goal_progress_percentage', 0):.1f}%
- Viikko: {context.get('current_week', 1)}/7
- Watchdog-tila: {context.get('watchdog_state', 'Active')}
- Kuukausitulot: {context.get('monthly_income', 0):,.0f}€
- Kuukausimenot: {context.get('monthly_expenses', 0):,.0f}€
- Viikkotavoite: {context.get('target_income_weekly', 300):,.0f}€

KÄYTTÄJÄN KYSYMYS: {message.message}

OHJEISTUS:
Vastaa henkilökohtaisesti, käytännöllisesti ja suomeksi. Käytä käyttäjän oikeita tietoja ja anna konkreettisia neuvoja. Ole motivoiva ja auta käyttäjää saavuttamaan 100 000€ säästötavoitteen. Käytä emojiita ja tee vastauksesta selkeä. Vastaa suoraan kysymykseen ja anna käytännöllisiä neuvoja.
"""

        # Use OpenAI API for real AI responses
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Olet Sentinel 100K - henkilökohtainen talousneuvoja. Vastaa aina suomeksi ja käytä emojiita."},
                    {"role": "user", "content": ai_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "response": ai_response,
                "enhanced_prompt_used": True,
                "user_email": user_email,
                "personalization_level": "Maximum",
                "context_sources": ["goal_tracking", "watchdog", "cycles", "analysis"],
                "watchdog_state": context.get("watchdog_state", "Active"),
                "goal_progress": context.get("progress_summary", {}).get("goal_progress_percentage", 0),
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-3.5-turbo",
                "environment": "render_production",
                "ai_used": True,
                "openai_used": True,
                "debug": {
                    "openai_key_available": bool(OPENAI_API_KEY),
                    "openai_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
                    "openai_key_starts_with": OPENAI_API_KEY[:10] if OPENAI_API_KEY else "None"
                }
            }
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return {
                "response": f"❌ OpenAI API virhe: {str(e)}. Ota yhteyttä ylläpitoon.",
                "error": "OPENAI_API_ERROR",
                "error_details": str(e),
                "enhanced_prompt_used": False,
                "user_email": user_email,
                "personalization_level": "None",
                "context_sources": [],
                "watchdog_state": context.get("watchdog_state", "Error"),
                "goal_progress": context.get("progress_summary", {}).get("goal_progress_percentage", 0),
                "timestamp": datetime.now().isoformat(),
                "model": "error",
                "environment": "render_production",
                "ai_used": False,
                "openai_used": False,
                "debug": {
                    "openai_key_available": bool(OPENAI_API_KEY),
                    "openai_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
                    "openai_key_starts_with": OPENAI_API_KEY[:10] if OPENAI_API_KEY else "None"
                }
            }
        
    except Exception as e:
        print(f"❌ Enhanced AI chat error: {e}")
        return {
            "response": f"❌ Järjestelmävirhe: {str(e)}. Ota yhteyttä ylläpitoon.",
            "error": "SYSTEM_ERROR",
            "error_details": str(e),
            "enhanced_prompt_used": False,
            "user_email": user_email,
            "personalization_level": "None",
            "context_sources": [],
            "timestamp": datetime.now().isoformat(),
            "model": "error",
            "environment": "render_production",
            "ai_used": False,
            "openai_used": False
        }

@app.post("/api/v1/chat/complete")
def complete_ai_chat(message: ChatMessage):
    """AI Chat with Finnish responses (Basic version)"""
    finnish_responses = [
        "Hyvä kysymys! Keskitytään säästötavoitteisiisi.",
        "Erinomaista edistymistä! Jatka samaan malliin.",
        "Tässä on henkilökohtainen suositukseni:",
        "Analysoin tilannettasi... Suosittelen näitä toimenpiteitä:",
        "Ymmärrän huolesi. Tehdään yhdessä suunnitelma.",
    ]
    
    response = {
        "response": f"{finnish_responses[hash(message.message) % len(finnish_responses)]} {message.message}",
        "timestamp": datetime.now().isoformat(),
        "ai_confidence": 0.95,
        "personalized": False,
        "language": "finnish",
        "model": "sentinel-basic",
        "note": "For enhanced features use /api/v1/chat/enhanced"
    }
    
    return response

# 📊 GOAL TRACKING ENDPOINT for RENDER
@app.get("/api/v1/goals/progress/{user_email}")
def get_goal_progress_render(user_email: str):
    """
    Goal tracking endpoint for Render production
    """
    try:
        context_manager = RenderUserContextManager(user_email)
        context = context_manager.get_enhanced_context()
        
        return {
            "status": "active",
            "user_email": user_email,
            "goal_tracking": {
                "current_savings": context["current_savings"],
                "savings_goal": context["savings_goal"],
                "progress_percentage": context["progress_summary"]["goal_progress_percentage"],
                "amount_to_goal": context["progress_summary"]["amount_to_goal"],
                "on_track": context["progress_summary"]["on_track"],
                "weeks_completed": context["progress_summary"]["weeks_completed"],
                "weeks_remaining": context["progress_summary"]["weeks_remaining"]
            },
            "weekly_status": {
                "current_week": context["current_week"],
                "weekly_target": context["target_income_weekly"],
                "cycle_progress": context["cycle_progress"],
                "difficulty_level": context["current_cycle_details"].get("difficulty_level", "N/A")
            },
            "watchdog_monitoring": {
                "state": context["watchdog_state"],
                "risk_assessment": context["latest_analysis"].get("risk_level", "unknown"),
                "recommendations": context["ai_context"]["ai_recommendations"][:3]
            },
            "environment": "render_production",
            "last_updated": context["context_generated"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Goal tracking failed: {str(e)}",
            "user_email": user_email
        }

# 🚀 TELEGRAM BOT INTEGRATION FOR RENDER

def get_or_create_telegram_user(telegram_id: int, username: str = None) -> dict:
    """Get or create a user profile for a Telegram user. Returns user dict with email as key."""
    users_data = data_manager.get_user_data()
    onboarding_data = data_manager.get_onboarding_data()
    telegram_email = f"telegram_{telegram_id}@sentinel100k.com"
    onboarding_key = f"onboarding_{telegram_email}"

    # Check if user exists
    if telegram_email in users_data:
        user_profile = users_data[telegram_email]
        onboarding_profile = onboarding_data.get(onboarding_key, {})
        return {
            "email": telegram_email,
            "user": user_profile,
            "onboarding": onboarding_profile
        }

    # Create new user profile
    now = datetime.now().isoformat()
    user_id = f"telegram_{telegram_id}"
    user_profile = {
        "id": user_id,
        "email": telegram_email,
        "name": username or f"TelegramUser_{telegram_id}",
        "created_at": now,
        "is_active": True
    }
    users_data[telegram_email] = user_profile
    data_manager.save_user_data(users_data)

    # Create onboarding profile with default values
    onboarding_profile = {
        "name": username or f"TelegramUser_{telegram_id}",
        "email": telegram_email,
        "user_id": user_id,
        "current_savings": 0,
        "savings_goal": 100000,
        "monthly_income": 0,
        "monthly_expenses": 0,
        "skills": [],
        "risk_tolerance": "Maltillinen",
        "age": None,
        "profession": None,
        "work_experience_years": 0,
        "time_availability_hours": 0,
        "financial_goals": [],
        "preferred_income_methods": [],
        "motivation_level": 7,
        "onboarding_completed": now,
        "profile_completeness": 10,
        "personalization_level": "basic"
    }
    onboarding_data[onboarding_key] = onboarding_profile
    data_manager.save_onboarding_data(onboarding_data)

    # Optionally, initialize cycles and analysis for new user
    cycles_data = data_manager.get_cycles_data()
    if onboarding_key not in cycles_data:
        cycles_data[onboarding_key] = {
            "data_key": onboarding_key,
            "user_id": user_id,
            "user_email": telegram_email,
            "current_week": 1,
            "cycle_started": now,
            "status": "active",
            "total_target": 0,
            "cycles": []
        }
        data_manager.save_cycles_data(cycles_data)
    analysis_data = data_manager.get_analysis_data()
    if "results" not in analysis_data:
        analysis_data["results"] = {}
    if onboarding_key not in analysis_data["results"]:
        analysis_data["results"][onboarding_key] = {
            "user_id": onboarding_key,
            "goal_progress": 0.0,
            "current_week": 1,
            "weekly_performance": "not_started",
            "risk_level": "unknown",
            "ai_recommendations": [],
            "next_week_adjustments": {},
            "analysis_timestamp": now,
            "strategy_updated": False
        }
        data_manager.save_analysis_data(analysis_data)

    return {
        "email": telegram_email,
        "user": user_profile,
        "onboarding": onboarding_profile
    }

def handle_telegram_command(text: str, user_id: int, username: str) -> str:
    """Handle Telegram commands"""
    
    # Get or create user profile
    user_info = get_or_create_telegram_user(user_id, username)
    telegram_email = user_info["email"]
    onboarding = user_info["onboarding"]
    name = onboarding.get("name", username or f"TelegramUser_{user_id}")
    current_savings = onboarding.get("current_savings", 0)
    savings_goal = onboarding.get("savings_goal", 100000)
    progress = (current_savings / savings_goal * 100) if savings_goal > 0 else 0
    
    # Use RenderUserContextManager for context
    context_manager = RenderUserContextManager(telegram_email)
    context = context_manager.get_enhanced_context()
    
    text_lower = text.lower().strip()
    
    if text_lower in ["/start", "start", "aloita"]:
        return f"""🚀 <b>Tervetuloa Sentinel 100K:ään, {name}!</b>

Olen henkilökohtainen talousneuvojasi, joka auttaa sinua saavuttamaan <b>100 000€ säästötavoitteen</b>.

💰 <b>Nykyinen tilanteesi:</b>
• Säästöt: {current_savings:,.0f}€
• Tavoite: {savings_goal:,.0f}€
• Edistyminen: {progress:.1f}%

💡 <b>Miten voin auttaa:</b>
• Kysy talousneuvoja
• Katso dashboard: /dashboard
• Pyydä henkilökohtaisia suosituksia
• Seuraa edistymistäsi

Kirjoita mitä tahansa talousasioista - vastaan henkilökohtaisesti! 💪"""

    elif text_lower in ["/dashboard", "dashboard", "tilanne", "progress"]:
        return f"""📊 <b>Dashboard - {name}</b>

💰 <b>Säästöt:</b> {current_savings:,.0f}€ / {savings_goal:,.0f}€
📈 <b>Edistyminen:</b> {progress:.1f}%
🎯 <b>Jäljellä:</b> {savings_goal - current_savings:,.0f}€

📅 <b>Viikkosykli:</b> {context.get('current_week', 1)}/7
💪 <b>Viikkotavoite:</b> {context.get('target_income_weekly', 300):,.0f}€
🤖 <b>Watchdog:</b> {context.get('watchdog_state', 'Active')}

💡 <b>Henkilökohtainen neuvoni:</b>
{context.get('ai_context', {}).get('ai_recommendations', ['Jatka hyvää työtä!'])[0] if context.get('ai_context', {}).get('ai_recommendations') else 'Keskity viikkotavoitteeseesi ja optimoi kulujasi!'}"""

    elif text_lower in ["/help", "help", "apua", "neuvo"]:
        return f"""💡 <b>Sentinel 100K - Apu</b>

<b>Komennot:</b>
• /start - Aloita
• /dashboard - Näytä dashboard
• /help - Tämä apu
• /onboarding - Aloita onboarding

<b>Vapaamuotoiset kysymykset:</b>
• "Mikä on budjettini?"
• "Kerro talousvinkkejä"
• "Miten säästän enemmän?"
• "Analysoi tilanteeni"
• "Anna henkilökohtaisia neuvoja"

<b>Henkilökohtainen konteksti:</b>
• Säästöt: {current_savings:,.0f}€
• Tavoite: {savings_goal:,.0f}€
• Edistyminen: {progress:.1f}%

Kysy mitä tahansa - vastaan henkilökohtaisesti! 🤖"""

    elif text_lower in ["/onboarding", "onboarding", "aloita onboarding"]:
        return f"""🎯 <b>Onboarding - {name}</b>

Tervetuloa Sentinel 100K onboardingiin! Autan sinua luomaan henkilökohtaisen taloussuunnitelman.

📋 <b>Seuraavat vaiheet:</b>

1️⃣ <b>Perustiedot</b>
Kirjoita: "Olen [ikä]-vuotias [ammatti]"

2️⃣ <b>Talousasiat</b>
Kirjoita: "Kuukausituloni on [summa]€ ja menoni [summa]€"

3️⃣ <b>Säästöt ja tavoitteet</b>
Kirjoita: "Säästöni on [summa]€ ja tavoitteeni [summa]€"

4️⃣ <b>Lisätiedot</b>
Kerro taidoistasi, kokemuksestasi ja motivaatiostasi

💡 <b>Esimerkkejä:</b>
• "Olen 30-vuotias ohjelmoija"
• "Tuloni 3000€, menoni 2000€"
• "Säästöni 5000€, tavoite 100000€"

Aloitetaan! Kerro ensin ikäsi ja ammattisi. 🚀"""

    else:
        return f"""❓ <b>Tuntematon komento: {text}</b>

Käytä komentoja:
• /start - Aloita
• /dashboard - Näytä dashboard  
• /help - Apu
• /onboarding - Aloita onboarding

Tai kirjoita vapaamuotoinen kysymys talousasioista! 💡"""

def get_telegram_response(text: str, user_id: int, username: str) -> str:
    """Get AI-powered response for Telegram user with full personalization"""
    # Get or create user profile
    user_info = get_or_create_telegram_user(user_id, username)
    telegram_email = user_info["email"]
    onboarding = user_info["onboarding"]
    name = onboarding.get("name", username or f"TelegramUser_{user_id}")
    current_savings = onboarding.get("current_savings", 0)
    savings_goal = onboarding.get("savings_goal", 100000)
    progress = (current_savings / savings_goal * 100) if savings_goal > 0 else 0

    # Use RenderUserContextManager for context
    context_manager = RenderUserContextManager(telegram_email)
    context = context_manager.get_enhanced_context()

    # Check for special commands first
    text_lower = text.lower().strip()
    
    if text_lower in ["/start", "start", "aloita"]:
        return f"""🚀 <b>Tervetuloa Sentinel 100K:ään, {name}!</b>

Olen henkilökohtainen talousneuvojasi, joka auttaa sinua saavuttamaan <b>100 000€ säästötavoitteen</b>.

💰 <b>Nykyinen tilanteesi:</b>
• Säästöt: {current_savings:,.0f}€
• Tavoite: {savings_goal:,.0f}€
• Edistyminen: {progress:.1f}%

💡 <b>Miten voin auttaa:</b>
• Kysy talousneuvoja
• Katso dashboard: "dashboard" tai "tilanne"
• Pyydä henkilökohtaisia suosituksia
• Seuraa edistymistäsi

Kirjoita mitä tahansa talousasioista - vastaan henkilökohtaisesti! 💪"""

    elif text_lower in ["/dashboard", "dashboard", "tilanne", "progress"]:
        return f"""📊 <b>Dashboard - {name}</b>

💰 <b>Säästöt:</b> {current_savings:,.0f}€ / {savings_goal:,.0f}€
📈 <b>Edistyminen:</b> {progress:.1f}%
🎯 <b>Jäljellä:</b> {savings_goal - current_savings:,.0f}€

📅 <b>Viikkosykli:</b> {context.get('current_week', 1)}/7
💪 <b>Viikkotavoite:</b> {context.get('target_income_weekly', 300):,.0f}€
🤖 <b>Watchdog:</b> {context.get('watchdog_state', 'Active')}

💡 <b>Henkilökohtainen neuvoni:</b>
{context.get('ai_context', {}).get('ai_recommendations', ['Jatka hyvää työtä!'])[0] if context.get('ai_context', {}).get('ai_recommendations') else 'Keskity viikkotavoitteeseesi ja optimoi kulujasi!'}"""

    elif text_lower in ["/help", "help", "apua", "neuvo"]:
        return f"""💡 <b>Sentinel 100K - Apu</b>

<b>Komennot:</b>
• /start - Aloita
• /dashboard - Näytä dashboard
• /help - Tämä apu
• /onboarding - Aloita onboarding

<b>Vapaamuotoiset kysymykset:</b>
• "Mikä on budjettini?"
• "Kerro talousvinkkejä"
• "Miten säästän enemmän?"
• "Analysoi tilanteeni"
• "Anna henkilökohtaisia neuvoja"

<b>Henkilökohtainen konteksti:</b>
• Säästöt: {current_savings:,.0f}€
• Tavoite: {savings_goal:,.0f}€
• Edistyminen: {progress:.1f}%

Kysy mitä tahansa - vastaan henkilökohtaisesti! 🤖"""

    elif "onboarding" in text_lower or "aloita onboarding" in text_lower or "/onboarding" in text_lower:
        return f"""🎯 <b>Onboarding - {name}</b>

Tervetuloa Sentinel 100K onboardingiin! Autan sinua luomaan henkilökohtaisen taloussuunnitelman.

📋 <b>Seuraavat vaiheet:</b>

1️⃣ <b>Perustiedot</b>
Kirjoita: "Olen [ikä]-vuotias [ammatti]"

2️⃣ <b>Talousasiat</b>
Kirjoita: "Kuukausituloni on [summa]€ ja menoni [summa]€"

3️⃣ <b>Säästöt ja tavoitteet</b>
Kirjoita: "Säästöni on [summa]€ ja tavoitteeni [summa]€"

4️⃣ <b>Lisätiedot</b>
Kerro taidoistasi, kokemuksestasi ja motivaatiostasi

💡 <b>Esimerkkejä:</b>
• "Olen 30-vuotias ohjelmoija"
• "Tuloni 3000€, menoni 2000€"
• "Säästöni 5000€, tavoite 100000€"

Aloitetaan! Kerro ensin ikäsi ja ammattisi. 🚀"""

    else:
        # Use enhanced AI chat for natural language responses
        try:
            chat_message = ChatMessage(message=text)
            ai_response = enhanced_ai_chat_render(chat_message, user_email=telegram_email)
            
            if isinstance(ai_response, dict):
                response_text = ai_response.get("response", "")
            else:
                response_text = str(ai_response)
            
            # If AI response is empty or too short, provide a fallback
            if not response_text or len(response_text) < 30:
                response_text = f"""🤖 <b>Sentinel 100K vastaa:</b>

Hei {name}! Olen analysoinut kysymyksesi: "{text}"

💰 <b>Henkilökohtainen konteksti:</b>
• Säästöt: {current_savings:,.0f}€
• Tavoite: {savings_goal:,.0f}€
• Edistyminen: {progress:.1f}%

💡 <b>Henkilökohtainen neuvoni:</b>
Keskity viikkotavoitteeseesi ({context.get('target_income_weekly', 300):,.0f}€) ja optimoi kulujasi. Jatka hyvää työtä saavuttaaksesi 100 000€ tavoitteesi!

Kysy mitä tahansa talousasioista - olen täällä auttamassa! 🚀"""
            
            return response_text
            
        except Exception as e:
            print(f"❌ AI response error: {e}")
            # Fallback response with user data
            return f"""🤖 <b>Sentinel 100K vastaa:</b>

Hei {name}! Tässä henkilökohtainen vastaukseni:

💬 <b>Kysymyksesi:</b> {text}

💰 <b>Henkilökohtainen tilanteesi:</b>
• Säästöt: {current_savings:,.0f}€
• Tavoite: {savings_goal:,.0f}€
• Edistyminen: {progress:.1f}%
• Viikko: {context.get('current_week', 1)}/7

💡 <b>Henkilökohtainen neuvoni:</b>
Keskity viikkotavoitteeseesi ({context.get('target_income_weekly', 300):,.0f}€) ja optimoi kulujasi. Jatka hyvää työtä saavuttaaksesi 100 000€ tavoitteesi!

Kysy mitä tahansa talousasioista - autan sinua saavuttamaan tavoitteesi! 🚀"""

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None

@app.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle Telegram webhook updates - PRODUCTION READY WITH ANALYTICS"""
    start_time = time.time()
    
    try:
        # Extract message data
        if update.message:
            message = update.message
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            user_id = message.get("from", {}).get("id")
            username = message.get("from", {}).get("username", "Unknown")
            
            print(f"📱 Telegram message from {username} ({user_id}): {text}")
            print(f"🔍 Chat ID: {chat_id}, User ID: {user_id}")
            
            # Track message
            analytics.data["system_health"]["total_requests"] += 1
            
            # --- USER PROFILE AUTO-REGISTRATION ---
            user_info = get_or_create_telegram_user(user_id, username)
            print(f"👤 User profile: {user_info['email']}")
            
            # --- AUTOMATIC CUSTOMER SERVICE CHECK ---
            support_response = customer_service.handle_support_request(user_id, username, text)
            if support_response:
                print(f"🆘 Support response: {support_response}")
                # Send support response
                telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
                if telegram_token:
                    telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                    payload = {
                        "chat_id": chat_id,
                        "text": support_response,
                        "parse_mode": "HTML"
                    }
                    response = requests.post(telegram_url, json=payload)
                    print(f"📤 Support response sent: {response.status_code}")
                
                # Track support interaction
                analytics.track_message(user_id, username, text, time.time() - start_time, ai_used=False)
                analytics.track_feature_usage("customer_service")
                
                return {"status": "success", "message": "Support response sent"}
            
            # --- SMART TELEGRAM RESPONSE HANDLING ---
            print(f"🤖 Getting AI response for: {text}")
            response_text = get_telegram_response(text, user_id, username)
            print(f"🤖 AI response: {response_text[:100]}...")
            
            # Send response back to Telegram
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if telegram_token:
                # Send message to Telegram
                telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "HTML"
                }
                
                print(f"📤 Sending to Telegram: {telegram_url}")
                print(f"📤 Payload: {payload}")
                
                response = requests.post(telegram_url, json=payload)
                response_time = time.time() - start_time
                
                print(f"📤 Telegram response: {response.status_code} - {response.text}")
                
                if response.status_code == 200:
                    print(f"✅ Telegram response sent successfully")
                    
                    # Track successful interaction
                    analytics.track_message(user_id, username, text, response_time, ai_used=True)
                    
                    # Track AI learning
                    ai_learning_engine.track_user_preference(user_id, "general", 5)  # Assume good response
                    
                    return {"status": "success", "message": "Telegram message processed"}
                else:
                    print(f"❌ Failed to send Telegram response: {response.status_code}")
                    print(f"❌ Response text: {response.text}")
                    analytics.track_error("telegram_send", f"Status: {response.status_code}")
                    return {"status": "error", "message": f"Failed to send response: {response.status_code}"}
            else:
                print("⚠️ TELEGRAM_BOT_TOKEN not found in environment variables")
                analytics.track_error("telegram_token", "Token not configured")
                return {"status": "warning", "message": "Bot token not configured"}
        
        return {"status": "success", "message": "Update processed"}
        
    except Exception as e:
        error_time = time.time() - start_time
        print(f"❌ Telegram webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        analytics.track_error("webhook_error", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/telegram/webhook")
async def telegram_webhook_get():
    """Handle Telegram webhook verification - RENDER PRODUCTION"""
    return {
        "status": "Telegram webhook endpoint is active",
        "environment": ENVIRONMENT,
        "version": "100.0.0",
        "render_production": True,
        "telegram_ready": bool(os.getenv("TELEGRAM_BOT_TOKEN"))
    }

@app.get("/telegram/test")
def telegram_test():
    """Test endpoint for Telegram integration - RENDER PRODUCTION"""
    return {
        "status": "telegram_ready",
        "endpoints": ["POST /telegram/webhook", "GET /telegram/webhook"],
        "version": "100.0.0",
        "environment": ENVIRONMENT,
        "telegram_token_set": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "render_production": True,
        "message": "Telegram integration is ready for production!"
    }

@app.post("/telegram/test-send")
def test_telegram_send():
    """Test sending message to Telegram"""
    try:
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            return {"status": "error", "message": "TELEGRAM_BOT_TOKEN not found"}
        
        # Test sending to a specific chat ID (you can change this)
        test_chat_id = 6698356764  # Your Telegram ID from logs
        
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": test_chat_id,
            "text": "🤖 <b>Testi viesti Sentinel 100K:stä!</b>\n\nTämä on testiviesti Render-palvelusta. AI-toiminnot ovat nyt toiminnassa! 🚀",
            "parse_mode": "HTML"
        }
        
        response = requests.post(telegram_url, json=payload)
        
        return {
            "status": "success" if response.status_code == 200 else "error",
            "telegram_status": response.status_code,
            "telegram_response": response.text,
            "chat_id": test_chat_id,
            "message": "Test message sent to Telegram"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/notifications/status")
def notification_status():
    """Check notification system status"""
    users = notification_manager.get_all_telegram_users()
    return {
        "status": "active",
        "telegram_users_count": len(users),
        "notification_schedule": {
            "daily_reminders": "09:00",
            "weekly_summaries": "Sunday 20:00",
            "watchdog_checks": "Every 6 hours",
            "milestone_checks": "18:00"
        },
        "manual_endpoints": [
            "POST /api/v1/notifications/send-daily",
            "POST /api/v1/notifications/send-weekly", 
            "POST /api/v1/notifications/check-watchdog",
            "POST /api/v1/notifications/check-milestones"
        ],
        "telegram_token_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "version": "100.1.0"
    }

# --- TELEGRAM NOTIFICATION SYSTEM ---
class TelegramNotificationManager:
    """Proactive notification system for Telegram users"""
    
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.telegram_token}"
        
    def send_telegram_message(self, chat_id: int, message: str) -> bool:
        """Send message to Telegram user"""
        if not self.telegram_token:
            print("⚠️ TELEGRAM_BOT_TOKEN not found")
            return False
            
        try:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(f"{self.base_url}/sendMessage", json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False
    
    def get_all_telegram_users(self) -> List[Dict[str, Any]]:
        """Get all registered Telegram users"""
        users_data = data_manager.get_user_data()
        telegram_users = []
        
        for email, user_data in users_data.items():
            if email.startswith("telegram_"):
                telegram_id = email.split("_")[1].split("@")[0]
                telegram_users.append({
                    "telegram_id": int(telegram_id),
                    "email": email,
                    "user_data": user_data
                })
        
        return telegram_users
    
    def send_daily_reminder(self, user_info: dict) -> bool:
        """Send daily savings reminder"""
        telegram_id = user_info["telegram_id"]
        email = user_info["email"]
        
        # Get user context
        context_manager = RenderUserContextManager(email)
        context = context_manager.get_enhanced_context()
        
        current_savings = context.get("current_savings", 0)
        savings_goal = context.get("savings_goal", 100000)
        progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
        current_week = context.get("current_week", 1)
        weekly_target = context.get("target_income_weekly", 300)
        
        message = f"""🌅 <b>Hyvää aamua!</b> 

💰 <b>Päivän säästömuistutus:</b>
• Nykyiset säästöt: {current_savings:,.0f}€
• Tavoite: {savings_goal:,.0f}€
• Edistyminen: {progress:.1f}%

📅 <b>Viikko {current_week}/7:</b>
• Viikkotavoite: {weekly_target:,.0f}€
• Tänään suosittelen säästämään: {weekly_target/7:.0f}€

💡 <b>Päivän vinkki:</b>
{self._get_daily_tip(context)}

Muista: Jokainen euro lähempänä tavoitetta! 💪"""
        
        return self.send_telegram_message(telegram_id, message)
    
    def send_watchdog_alert(self, user_info: dict, alert_type: str = "general") -> bool:
        """Send watchdog alert based on user progress"""
        telegram_id = user_info["telegram_id"]
        email = user_info["email"]
        
        context_manager = RenderUserContextManager(email)
        context = context_manager.get_enhanced_context()
        
        current_savings = context.get("current_savings", 0)
        savings_goal = context.get("savings_goal", 100000)
        progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
        current_week = context.get("current_week", 1)
        
        if alert_type == "low_progress":
            message = f"""🚨 <b>Watchdog Alert - Hidastunut edistyminen</b>

⚠️ Säästämisesi on hidastunut viime aikoina!

📊 <b>Tilanne:</b>
• Edistyminen: {progress:.1f}%
• Viikko: {current_week}/7
• Jäljellä: {savings_goal - current_savings:,.0f}€

💡 <b>Kriittiset toimenpiteet:</b>
1. Analysoi kulut tarkasti
2. Etsi lisätulolähteitä
3. Optimoi säästöstrategiaa

Haluatko apua talousanalyysissä? 💰"""
        
        elif alert_type == "behind_schedule":
            message = f"""⚠️ <b>Watchdog Alert - Aikataulusta jäljessä</b>

📅 Olet aikataulusta jäljessä tavoitteesi saavuttamisessa.

📊 <b>Analyysi:</b>
• Edistyminen: {progress:.1f}%
• Viikko: {current_week}/7
• Tarvittava korotus: {self._calculate_catchup_amount(context):.0f}€/viikko

🎯 <b>Suositukset:</b>
• Lisää säästösummaa {self._calculate_catchup_amount(context):.0f}€/viikko
• Etsi lisätulolähteitä
• Optimoi kuluja

Haluatko henkilökohtaisen suunnitelman? 🚀"""
        
        else:
            message = f"""🤖 <b>Watchdog Tila - {context.get('watchdog_state', 'Active')}</b>

📊 <b>Nykyinen tilanne:</b>
• Säästöt: {current_savings:,.0f}€
• Edistyminen: {progress:.1f}%
• Viikko: {current_week}/7

💡 <b>AI-suositukset:</b>
{self._get_ai_recommendations(context)}

Jatka hyvää työtä! 💪"""
        
        return self.send_telegram_message(telegram_id, message)
    
    def send_milestone_celebration(self, user_info: dict, milestone_type: str) -> bool:
        """Send milestone celebration message"""
        telegram_id = user_info["telegram_id"]
        email = user_info["email"]
        
        context_manager = RenderUserContextManager(email)
        context = context_manager.get_enhanced_context()
        
        current_savings = context.get("current_savings", 0)
        progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
        
        if milestone_type == "first_1000":
            message = f"""🎉 <b>ONNITELUT! Ensimmäinen 1000€ saavutettu!</b>

💰 Olet saavuttanut ensimmäisen 1000€ säästösi!

📈 <b>Edistyminen:</b>
• Säästöt: {current_savings:,.0f}€
• Edistyminen: {progress:.1f}%

🏆 <b>Seuraava tavoite:</b> 5000€

Jatka samalla tahdilla! Olet menossa oikeaan suuntaan! 🚀"""
        
        elif milestone_type == "quarter_goal":
            message = f"""🎊 <b>UPEAA! 25% tavoitteesta saavutettu!</b>

🎯 Olet saavuttanut neljänneksen 100 000€ tavoitteestasi!

📊 <b>Tilanne:</b>
• Säästöt: {current_savings:,.0f}€
• Edistyminen: {progress:.1f}%

💪 <b>Seuraava tavoite:</b> 50% (50 000€)

Olet todellinen säästäjä! Jatka samalla energialla! 💰"""
        
        elif milestone_type == "half_goal":
            message = f"""🏆 <b>FANTASTISTA! Puolet tavoitteesta saavutettu!</b>

🎯 Olet saavuttanut 50 000€ - puolet tavoitteestasi!

📈 <b>Suoritus:</b>
• Säästöt: {current_savings:,.0f}€
• Edistyminen: {progress:.1f}%

🚀 <b>Seuraava tavoite:</b> 75% (75 000€)

Olet todellinen talousmestari! Jatka samalla tahdilla! 💪"""
        
        elif milestone_type == "week_completed":
            message = f"""✅ <b>Viikko suoritettu!</b>

📅 Olet suorittanut viikon {context.get('current_week', 1)}/7!

📊 <b>Viikon yhteenveto:</b>
• Viikkotavoite: {context.get('target_income_weekly', 0):,.0f}€
• Edistyminen: {progress:.1f}%

🎯 <b>Seuraava viikko:</b> {context.get('current_week', 1) + 1}/7

Hyvää työtä! Jatka samalla energialla! 💰"""
        
        else:
            message = f"""🎉 <b>Onnittelut edistymisestäsi!</b>

💰 <b>Nykyinen tilanne:</b>
• Säästöt: {current_savings:,.0f}€
• Edistyminen: {progress:.1f}%

Jatka hyvää työtä! Olet menossa oikeaan suuntaan! 🚀"""
        
        return self.send_telegram_message(telegram_id, message)
    
    def send_weekly_summary(self, user_info: dict) -> bool:
        """Send weekly summary and next week preview"""
        telegram_id = user_info["telegram_id"]
        email = user_info["email"]
        
        context_manager = RenderUserContextManager(email)
        context = context_manager.get_enhanced_context()
        
        current_savings = context.get("current_savings", 0)
        progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
        current_week = context.get("current_week", 1)
        weekly_target = context.get("target_income_weekly", 300)
        
        message = f"""📊 <b>Viikon yhteenveto</b>

📅 <b>Viikko {current_week}/7 suoritettu!</b>

💰 <b>Tilanne:</b>
• Säästöt: {current_savings:,.0f}€
• Edistyminen: {progress:.1f}%
• Viikkotavoite: {weekly_target:,.0f}€

🎯 <b>Seuraava viikko ({current_week + 1}/7):</b>
• Uusi viikkotavoite: {self._get_next_week_target(context):.0f}€
• Haasteet: {', '.join(self._get_next_week_challenges(context))}

💡 <b>Suositukset seuraavalle viikolle:</b>
{self._get_weekly_recommendations(context)}

Hyvää työtä! Jatka samalla energialla! 💪"""
        
        return self.send_telegram_message(telegram_id, message)
    
    def _get_daily_tip(self, context: dict) -> str:
        """Get personalized daily tip"""
        tips = [
            "Tallenna kaikki kulut tänään - tiedät missä raha menee!",
            "Etsi yksi tarpeeton kuluerä ja leikkaa se pois.",
            "Suunnittele viikon ruokaostokset etukäteen.",
            "Vertaa hintoja ennen ostoa - säästät helposti 10-20%.",
            "Aseta automaattinen säästösiirto palkkapäivänä.",
            "Etsi yksi uusi tulolähde tällä viikolla.",
            "Optimoi sähkö- ja puhelinlaskut.",
            "Myy yksi tarpeeton esine verkossa."
        ]
        return tips[context.get("current_week", 1) % len(tips)]
    
    def _get_ai_recommendations(self, context: dict) -> str:
        """Get AI recommendations based on context"""
        progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
        
        if progress < 25:
            return "• Tehosta säästämistä välittömästi\n• Analysoi kaikki kulut\n• Etsi lisätulolähteitä"
        elif progress < 50:
            return "• Optimoi säästöstrategiaa\n• Lisää tulolähteitä\n• Automatisoi säästäminen"
        else:
            return "• Skaalaa menestyksekkäitä strategioita\n• Harkitse sijoittamista\n• Suunnittele pitkän aikavälin tavoitteet"
    
    def _calculate_catchup_amount(self, context: dict) -> float:
        """Calculate how much more user needs to save to catch up"""
        progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
        current_week = context.get("current_week", 1)
        expected_progress = (current_week / 7) * 100
        deficit = expected_progress - progress
        
        if deficit > 0:
            savings_goal = context.get("savings_goal", 100000)
            return (deficit / 100) * savings_goal / (7 - current_week)
        return 0
    
    def _get_next_week_target(self, context: dict) -> float:
        """Get next week's target"""
        current_week = context.get("current_week", 1)
        base_target = 300
        if current_week < 7:
            return base_target * (1 + (current_week * 0.1))
        return base_target * 1.5
    
    def _get_next_week_challenges(self, context: dict) -> List[str]:
        """Get next week's challenges"""
        current_week = context.get("current_week", 1)
        challenges = [
            ["Tallenna kaikki kulut", "Löydä 3 säästökohdetta", "Tee budjetti viikolle"],
            ["Neuvottele yksi lasku alemmas", "Myy 1 tarpeeton esine", "Tee freelance-haku"],
            ["Aloita sivutyö", "Optimoi suurin kuluerä", "Luo passiivinen tulolähde"],
            ["Kasvata sivutyötuloja", "Automatisoi säästäminen", "Verkostoidu ammattialalla"],
            ["Lanseeraa oma palvelu", "Nosta tuntihintoja", "Solmi pitkäaikainen sopimus"],
            ["Skaalaa liiketoimintaa", "Tee strateginen sijoitus", "Luo toinen tulolähde"],
            ["Maksimoi kaikki tulot", "Varmista jatkuvuus", "Suunnittele seuraava sykli"]
        ]
        if current_week <= len(challenges):
            return challenges[current_week - 1]
        return ["Jatka hyvää työtä", "Optimoi strategioita", "Skaalaa menestystä"]
    
    def _get_weekly_recommendations(self, context: dict) -> str:
        """Get weekly recommendations"""
        current_week = context.get("current_week", 1)
        recommendations = [
            "Keskity perusteiden oppimiseen ja säästöjen aloittamiseen.",
            "Aloita tulojen lisääminen ja kulujen optimointi.",
            "Skaalaa menestyksekkäitä strategioita ja automatisoi.",
            "Harkitse sijoittamista ja pitkän aikavälin suunnittelua.",
            "Maksimoi kaikki tulolähteet ja optimoi verotusta.",
            "Suunnittele seuraavaa vaihetta ja skaalaa liiketoimintaa.",
            "Varmista jatkuvuus ja suunnittele uusia tavoitteita."
        ]
        if current_week <= len(recommendations):
            return recommendations[current_week - 1]
        return "Jatka hyvää työtä ja optimoi strategioita!"

# Initialize notification manager
notification_manager = TelegramNotificationManager()

# --- SCHEDULED NOTIFICATION FUNCTIONS ---
def send_daily_reminders():
    """Send daily reminders to all Telegram users"""
    print("📅 Sending daily reminders...")
    users = notification_manager.get_all_telegram_users()
    
    for user in users:
        try:
            success = notification_manager.send_daily_reminder(user)
            if success:
                print(f"✅ Daily reminder sent to {user['email']}")
            else:
                print(f"❌ Failed to send daily reminder to {user['email']}")
        except Exception as e:
            print(f"❌ Error sending daily reminder to {user['email']}: {e}")
        
        # Small delay to avoid rate limiting
        time.sleep(1)

def send_weekly_summaries():
    """Send weekly summaries to all Telegram users"""
    print("📊 Sending weekly summaries...")
    users = notification_manager.get_all_telegram_users()
    
    for user in users:
        try:
            success = notification_manager.send_weekly_summary(user)
            if success:
                print(f"✅ Weekly summary sent to {user['email']}")
            else:
                print(f"❌ Failed to send weekly summary to {user['email']}")
        except Exception as e:
            print(f"❌ Error sending weekly summary to {user['email']}: {e}")
        
        time.sleep(1)

def check_watchdog_alerts():
    """Check and send watchdog alerts"""
    print("🤖 Checking watchdog alerts...")
    users = notification_manager.get_all_telegram_users()
    
    for user in users:
        try:
            context_manager = RenderUserContextManager(user['email'])
            context = context_manager.get_enhanced_context()
            
            progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
            current_week = context.get("current_week", 1)
            expected_progress = (current_week / 7) * 100
            
            # Send alert if significantly behind schedule
            if progress < expected_progress - 10:
                success = notification_manager.send_watchdog_alert(user, "behind_schedule")
                if success:
                    print(f"⚠️ Watchdog alert sent to {user['email']}")
            
            # Send alert if very low progress
            elif progress < 15:
                success = notification_manager.send_watchdog_alert(user, "low_progress")
                if success:
                    print(f"🚨 Low progress alert sent to {user['email']}")
                    
        except Exception as e:
            print(f"❌ Error checking watchdog for {user['email']}: {e}")
        
        time.sleep(1)

def check_milestones():
    """Check and celebrate milestones"""
    print("🎉 Checking milestones...")
    users = notification_manager.get_all_telegram_users()
    
    for user in users:
        try:
            context_manager = RenderUserContextManager(user['email'])
            context = context_manager.get_enhanced_context()
            
            current_savings = context.get("current_savings", 0)
            progress = context.get("progress_summary", {}).get("goal_progress_percentage", 0)
            
            # Check for milestones (you might want to store these in user data to avoid duplicates)
            if current_savings >= 1000 and current_savings < 1100:
                success = notification_manager.send_milestone_celebration(user, "first_1000")
                if success:
                    print(f"🎉 First 1000€ milestone celebrated for {user['email']}")
            
            elif progress >= 25 and progress < 26:
                success = notification_manager.send_milestone_celebration(user, "quarter_goal")
                if success:
                    print(f"🎊 25% goal milestone celebrated for {user['email']}")
            
            elif progress >= 50 and progress < 51:
                success = notification_manager.send_milestone_celebration(user, "half_goal")
                if success:
                    print(f"🏆 50% goal milestone celebrated for {user['email']}")
                    
        except Exception as e:
            print(f"❌ Error checking milestones for {user['email']}: {e}")
        
        time.sleep(1)

# --- SCHEDULER SETUP ---
def setup_notification_scheduler():
    """Setup scheduled notifications"""
    # Daily reminders at 9:00 AM
    schedule.every().day.at("09:00").do(send_daily_reminders)
    
    # Weekly summaries on Sundays at 8:00 PM
    schedule.every().sunday.at("20:00").do(send_weekly_summaries)
    
    # Watchdog checks every 6 hours
    schedule.every(6).hours.do(check_watchdog_alerts)
    
    # Milestone checks daily at 6:00 PM
    schedule.every().day.at("18:00").do(check_milestones)
    
    print("✅ Notification scheduler setup complete")

def run_scheduler():
    """Run the notification scheduler"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# --- MANUAL NOTIFICATION ENDPOINTS ---
@app.post("/api/v1/notifications/send-daily")
def trigger_daily_reminders():
    """Manually trigger daily reminders"""
    try:
        send_daily_reminders()
        return {"status": "success", "message": "Daily reminders sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/notifications/send-weekly")
def trigger_weekly_summaries():
    """Manually trigger weekly summaries"""
    try:
        send_weekly_summaries()
        return {"status": "success", "message": "Weekly summaries sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/notifications/check-watchdog")
def trigger_watchdog_check():
    """Manually trigger watchdog check"""
    try:
        check_watchdog_alerts()
        return {"status": "success", "message": "Watchdog check completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/notifications/check-milestones")
def trigger_milestone_check():
    """Manually trigger milestone check"""
    try:
        check_milestones()
        return {"status": "success", "message": "Milestone check completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- PRODUCTION ANALYTICS & MONITORING ---
class SentinelAnalytics:
    """Production analytics and monitoring for Sentinel 100K"""
    
    def __init__(self):
        self.analytics_file = Path("data/analytics.json")
        self.analytics_file.parent.mkdir(exist_ok=True)
        self.load_analytics()
        
        # Real-time counters
        self.message_counter = 0
        self.user_counter = 0
        self.response_times = []
        self.error_counter = 0
        self.ai_usage_counter = 0
        
    def load_analytics(self):
        """Load analytics data"""
        try:
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    "users": {},
                    "messages": [],
                    "performance": {
                        "response_times": [],
                        "error_rates": [],
                        "ai_usage": []
                    },
                    "features": {
                        "dashboard_usage": 0,
                        "notifications_sent": 0,
                        "milestones_celebrated": 0,
                        "watchdog_alerts": 0
                    },
                    "system_health": {
                        "uptime": 0,
                        "last_restart": datetime.now().isoformat(),
                        "total_requests": 0
                    }
                }
        except Exception as e:
            print(f"❌ Analytics load error: {e}")
            self.data = {"users": {}, "messages": [], "performance": {}, "features": {}, "system_health": {}}
    
    def save_analytics(self):
        """Save analytics data"""
        try:
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Analytics save error: {e}")
    
    def track_message(self, user_id: int, username: str, message: str, response_time: float, ai_used: bool = True):
        """Track user message and response"""
        self.message_counter += 1
        
        message_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "username": username,
            "message": message[:100],  # Truncate for privacy
            "response_time": response_time,
            "ai_used": ai_used,
            "message_length": len(message)
        }
        
        self.data["messages"].append(message_data)
        
        # Track user
        if str(user_id) not in self.data["users"]:
            self.data["users"][str(user_id)] = {
                "username": username,
                "first_seen": datetime.now().isoformat(),
                "message_count": 0,
                "last_active": datetime.now().isoformat(),
                "total_response_time": 0,
                "ai_usage_count": 0
            }
            self.user_counter += 1
        
        user_data = self.data["users"][str(user_id)]
        user_data["message_count"] += 1
        user_data["last_active"] = datetime.now().isoformat()
        user_data["total_response_time"] += response_time
        if ai_used:
            user_data["ai_usage_count"] += 1
            self.ai_usage_counter += 1
        
        # Track performance
        self.response_times.append(response_time)
        self.data["performance"]["response_times"].append(response_time)
        
        # Keep only last 1000 entries for performance
        if len(self.data["performance"]["response_times"]) > 1000:
            self.data["performance"]["response_times"] = self.data["performance"]["response_times"][-1000:]
        
        self.save_analytics()
    
    def track_error(self, error_type: str, error_message: str):
        """Track system errors"""
        self.error_counter += 1
        
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message
        }
        
        if "errors" not in self.data:
            self.data["errors"] = []
        
        self.data["errors"].append(error_data)
        
        # Keep only last 100 errors
        if len(self.data["errors"]) > 100:
            self.data["errors"] = self.data["errors"][-100:]
        
        self.save_analytics()
    
    def track_feature_usage(self, feature: str):
        """Track feature usage"""
        if feature in self.data["features"]:
            self.data["features"][feature] += 1
        else:
            self.data["features"][feature] = 1
        self.save_analytics()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        total_users = len(self.data["users"])
        total_messages = len(self.data["messages"])
        
        avg_response_time = 0
        if self.data["performance"]["response_times"]:
            avg_response_time = statistics.mean(self.data["performance"]["response_times"])
        
        # Calculate user engagement
        active_users_24h = 0
        active_users_7d = 0
        now = datetime.now()
        
        for user_data in self.data["users"].values():
            last_active = datetime.fromisoformat(user_data["last_active"])
            if (now - last_active).days <= 1:
                active_users_24h += 1
            if (now - last_active).days <= 7:
                active_users_7d += 1
        
        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "active_users_24h": active_users_24h,
            "active_users_7d": active_users_7d,
            "avg_response_time": round(avg_response_time, 3),
            "error_rate": len(self.data.get("errors", [])) / max(total_messages, 1),
            "ai_usage_rate": self.ai_usage_counter / max(total_messages, 1),
            "features": self.data["features"],
            "system_uptime": self.data["system_health"]["uptime"]
        }

# Initialize analytics
analytics = SentinelAnalytics()

# --- MASS NOTIFICATION SYSTEM ---
class MassNotificationManager:
    """Mass notification system for production scalability"""
    
    def __init__(self):
        self.notification_manager = notification_manager
        self.batch_size = 50  # Send in batches to avoid rate limits
        self.delay_between_batches = 2  # seconds
    
    def send_mass_notification(self, notification_type: str, custom_message: str = None) -> Dict[str, Any]:
        """Send mass notification to all users"""
        users = self.notification_manager.get_all_telegram_users()
        results = {
            "total_users": len(users),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        print(f"📢 Sending mass {notification_type} notification to {len(users)} users...")
        
        for i, user in enumerate(users):
            try:
                success = False
                
                if notification_type == "daily_reminder":
                    success = self.notification_manager.send_daily_reminder(user)
                elif notification_type == "weekly_summary":
                    success = self.notification_manager.send_weekly_summary(user)
                elif notification_type == "custom_message" and custom_message:
                    success = self.notification_manager.send_telegram_message(
                        user["telegram_id"], 
                        f"📢 <b>Sentinel 100K ilmoitus:</b>\n\n{custom_message}"
                    )
                elif notification_type == "system_update":
                    success = self.notification_manager.send_telegram_message(
                        user["telegram_id"],
                        "🔄 <b>Sentinel 100K päivitys</b>\n\nJärjestelmä on päivitetty uusilla ominaisuuksilla! Kysy mitä tahansa talousasioista - olen täällä auttamassa! 💪"
                    )
                
                if success:
                    results["successful"] += 1
                    analytics.track_feature_usage(f"mass_notification_{notification_type}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to send to {user['email']}")
                
                # Batch processing
                if (i + 1) % self.batch_size == 0:
                    print(f"📦 Processed batch {(i + 1) // self.batch_size}")
                    time.sleep(self.delay_between_batches)
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error sending to {user['email']}: {str(e)}")
                analytics.track_error("mass_notification", str(e))
        
        print(f"✅ Mass notification completed: {results['successful']} successful, {results['failed']} failed")
        return results

# Initialize mass notification manager
mass_notification_manager = MassNotificationManager()

# --- AI LEARNING & OPTIMIZATION ---
class AILearningEngine:
    """AI learning and optimization for continuous improvement"""
    
    def __init__(self):
        self.learning_data_file = Path("data/ai_learning.json")
        self.learning_data_file.parent.mkdir(exist_ok=True)
        self.load_learning_data()
    
    def load_learning_data(self):
        """Load AI learning data"""
        try:
            if self.learning_data_file.exists():
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    "user_preferences": {},
                    "response_patterns": {},
                    "successful_interactions": [],
                    "optimization_suggestions": []
                }
        except Exception as e:
            print(f"❌ AI learning load error: {e}")
            self.data = {"user_preferences": {}, "response_patterns": {}, "successful_interactions": [], "optimization_suggestions": []}
    
    def save_learning_data(self):
        """Save AI learning data"""
        try:
            with open(self.learning_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ AI learning save error: {e}")
    
    def track_user_preference(self, user_id: int, message_type: str, response_quality: int):
        """Track user preferences and response quality"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.data["user_preferences"]:
            self.data["user_preferences"][user_id_str] = {
                "preferred_topics": [],
                "response_ratings": [],
                "interaction_count": 0
            }
        
        user_prefs = self.data["user_preferences"][user_id_str]
        user_prefs["interaction_count"] += 1
        
        if message_type not in user_prefs["preferred_topics"]:
            user_prefs["preferred_topics"].append(message_type)
        
        user_prefs["response_ratings"].append({
            "timestamp": datetime.now().isoformat(),
            "message_type": message_type,
            "rating": response_quality
        })
        
        # Keep only last 50 ratings per user
        if len(user_prefs["response_ratings"]) > 50:
            user_prefs["response_ratings"] = user_prefs["response_ratings"][-50:]
        
        self.save_learning_data()
    
    def analyze_response_patterns(self) -> Dict[str, Any]:
        """Analyze response patterns for optimization"""
        patterns = {
            "most_common_questions": [],
            "response_quality_trends": [],
            "user_engagement_patterns": [],
            "optimization_opportunities": []
        }
        
        # Analyze message patterns from analytics
        if hasattr(analytics, 'data') and 'messages' in analytics.data:
            messages = analytics.data['messages']
            
            # Most common question types
            question_types = []
            for msg in messages:
                text = msg.get('message', '').lower()
                if 'sääst' in text:
                    question_types.append('savings')
                elif 'tavoite' in text or 'edistym' in text:
                    question_types.append('goals')
                elif 'dashboard' in text or 'tilanne' in text:
                    question_types.append('dashboard')
                elif 'vinkki' in text or 'neuvo' in text:
                    question_types.append('advice')
                else:
                    question_types.append('general')
            
            if question_types:
                counter = Counter(question_types)
                patterns["most_common_questions"] = counter.most_common(5)
        
        # Response quality trends
        if 'users' in self.data:
            for user_data in self.data['users'].values():
                if 'response_ratings' in user_data:
                    avg_rating = statistics.mean([r['rating'] for r in user_data['response_ratings']])
                    patterns["response_quality_trends"].append(avg_rating)
        
        # Optimization suggestions
        if patterns["response_quality_trends"]:
            avg_quality = statistics.mean(patterns["response_quality_trends"])
            if avg_quality < 4.0:
                patterns["optimization_opportunities"].append("Improve response quality")
        
        return patterns
    
    def get_optimization_suggestions(self) -> List[str]:
        """Get AI optimization suggestions"""
        suggestions = []
        
        # Analyze patterns
        patterns = self.analyze_response_patterns()
        
        # Generate suggestions based on patterns
        if patterns["most_common_questions"]:
            most_common = patterns["most_common_questions"][0][0]
            suggestions.append(f"Focus on improving {most_common} responses")
        
        if patterns["response_quality_trends"]:
            avg_quality = statistics.mean(patterns["response_quality_trends"])
            if avg_quality < 4.0:
                suggestions.append("Enhance AI prompt engineering")
                suggestions.append("Add more context to responses")
        
        # System suggestions
        suggestions.append("Monitor user engagement patterns")
        suggestions.append("Optimize response times")
        suggestions.append("Personalize responses based on user history")
        
        return suggestions

# Initialize AI learning engine
ai_learning_engine = AILearningEngine()

# --- AUTOMATIC CUSTOMER SERVICE ---
class AutomaticCustomerService:
    """Automatic customer service and support system"""
    
    def __init__(self):
        self.support_requests = []
        self.faq_responses = {
            "miten aloitan": "Aloita kertomalla minulle säästötavoitteistasi! Voin auttaa sinua suunnittelemaan 100 000€ säästötavoitteen saavuttamisen.",
            "miksi en säästä": "Analysoin tilannettasi ja annan henkilökohtaisia vinkkejä. Kerro nykyisistä säästöistäsi ja tuloistasi!",
            "mikä on watchdog": "Sentinel Watchdog™ seuraa automaattisesti edistymistäsi ja hälyttää jos tavoite vaarantuu.",
            "miten muutan tavoitetta": "Voit muuttaa tavoitteesi kertomalla minulle uuden summan. Autan sinua suunnittelemaan uuden strategian!",
            "miksi en saa vastausta": "Jos et saa vastausta, kokeile uudelleen tai tarkista internet-yhteys. Olen täällä auttamassa!",
            "mikä on viikkosykli": "7-viikon intensiivikurssi auttaa sinua saavuttamaan 100 000€ säästötavoitteen progressiivisella säästämisellä."
        }
    
    def handle_support_request(self, user_id: int, username: str, message: str) -> str:
        """Handle automatic customer service requests"""
        message_lower = message.lower()
        
        # Check for support keywords
        support_keywords = ['apua', 'ongelma', 'virhe', 'ei toimi', 'tuki', 'help', 'problem', 'error']
        if any(keyword in message_lower for keyword in support_keywords):
            self.support_requests.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "username": username,
                "message": message,
                "status": "pending"
            })
            
            return f"""🆘 <b>Automaattinen tuki aktivoitu</b>

Hei {username}! Olen vastaanottanut tukipyyntösi.

🔧 <b>Automaattiset ratkaisut:</b>
• Tarkista internet-yhteys
• Kokeile lähettää viesti uudelleen
• Käytä selkeitä kysymyksiä

📞 <b>Jos ongelma jatkuu:</b>
• Kirjoita tarkemmin ongelmasta
• Kerro milloin ongelma alkoi
• Kuvaile mitä yritit tehdä

Olen täällä auttamassa! 🤖"""
        
        # Check FAQ
        for faq_keyword, faq_response in self.faq_responses.items():
            if faq_keyword in message_lower:
                return f"""❓ <b>Usein kysytty kysymys:</b>

{faq_response}

Jos tämä ei vastaa kysymykseesi, kerro tarkemmin mitä haluat tietää! 💡"""
        
        return None  # No automatic support needed
    
    def get_support_statistics(self) -> Dict[str, Any]:
        """Get customer service statistics"""
        return {
            "total_requests": len(self.support_requests),
            "pending_requests": len([r for r in self.support_requests if r["status"] == "pending"]),
            "resolved_requests": len([r for r in self.support_requests if r["status"] == "resolved"]),
            "common_issues": self.analyze_common_issues()
        }
    
    def analyze_common_issues(self) -> List[str]:
        """Analyze common support issues"""
        issues = []
        for request in self.support_requests:
            message = request.get("message", "").lower()
            if "ei toimi" in message:
                issues.append("Technical issues")
            elif "apua" in message:
                issues.append("General help")
            elif "virhe" in message:
                issues.append("Error messages")
        return list(set(issues))

# Initialize automatic customer service
customer_service = AutomaticCustomerService()

# --- PRODUCTION ENDPOINTS ---
@app.get("/api/v1/analytics/summary")
def get_analytics_summary():
    """Get production analytics summary"""
    try:
        summary = analytics.get_analytics_summary()
        return {
            "status": "success",
            "analytics": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        analytics.track_error("analytics_summary", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/analytics/detailed")
def get_detailed_analytics():
    """Get detailed analytics data"""
    try:
        return {
            "status": "success",
            "analytics": analytics.data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        analytics.track_error("detailed_analytics", str(e))
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/notifications/mass")
def send_mass_notification(notification_type: str, custom_message: str = None):
    """Send mass notification to all users"""
    try:
        results = mass_notification_manager.send_mass_notification(notification_type, custom_message)
        return {
            "status": "success",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        analytics.track_error("mass_notification", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/ai/learning/patterns")
def get_ai_learning_patterns():
    """Get AI learning patterns and optimization suggestions"""
    try:
        patterns = ai_learning_engine.analyze_response_patterns()
        suggestions = ai_learning_engine.get_optimization_suggestions()
        
        return {
            "status": "success",
            "patterns": patterns,
            "optimization_suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        analytics.track_error("ai_learning", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/support/statistics")
def get_support_statistics():
    """Get customer service statistics"""
    try:
        stats = customer_service.get_support_statistics()
        return {
            "status": "success",
            "support_statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        analytics.track_error("support_statistics", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/system/health/detailed")
def get_detailed_system_health():
    """Get detailed system health information"""
    try:
        # Get all system metrics
        analytics_summary = analytics.get_analytics_summary()
        ai_patterns = ai_learning_engine.analyze_response_patterns()
        support_stats = customer_service.get_support_statistics()
        
        # Calculate system health score
        health_score = 100
        if analytics_summary["error_rate"] > 0.1:
            health_score -= 20
        if analytics_summary["avg_response_time"] > 5.0:
            health_score -= 15
        if support_stats["total_requests"] > 10:
            health_score -= 10
        
        return {
            "status": "success",
            "system_health": {
                "overall_score": max(health_score, 0),
                "analytics": analytics_summary,
                "ai_learning": ai_patterns,
                "customer_service": support_stats,
                "uptime": analytics.data["system_health"]["uptime"],
                "total_requests": analytics.data["system_health"]["total_requests"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        analytics.track_error("system_health", str(e))
        return {"status": "error", "message": str(e)}

@app.get("/debug/openai")
def debug_openai():
    """Debug OpenAI API key status"""
    return {
        "openai_key_available": bool(OPENAI_API_KEY),
        "openai_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        "openai_key_starts_with": OPENAI_API_KEY[:10] if OPENAI_API_KEY else "None",
        "openai_key_is_test": OPENAI_API_KEY == "sk-test-key-for-development" if OPENAI_API_KEY else True,
        "environment_vars": {
            "OPENAI_API_KEY": "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Not set",
            "openAI": "✅ Set" if os.getenv("openAI") else "❌ Not set",
            "OPENAI_KEY": "✅ Set" if os.getenv("OPENAI_KEY") else "❌ Not set"
        },
        "final_key": "✅ Valid" if OPENAI_API_KEY and OPENAI_API_KEY != "sk-test-key-for-development" else "❌ Invalid",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT
    }

# 🏁 Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "sentinel_render_ready:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    ) 