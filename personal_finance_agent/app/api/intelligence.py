"""
Intelligence API endpoints for AI services.
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from typing import Optional, Dict, Any
from datetime import datetime

from app.db.init_db import get_db
from app.services.idea_engine import IdeaEngine
from app.services.sentinel_watchdog_service import SentinelWatchdogService
from app.services.sentinel_learning_engine import SentinelLearningEngine
from app.services.event_bus import EventType, publish_event
from app.models import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

# Initialize AI services
idea_engine = IdeaEngine()
watchdog_service = SentinelWatchdogService()
learning_engine = SentinelLearningEngine()

@router.get("/ideas/daily/{user_email}")
async def get_daily_ideas(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get daily personalized income ideas"""
    try:
        # Get user profile
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create user profile for IdeaEngine
        user_profile = {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "skills": ["Programming", "Design", "Writing"],  # Default skills
            "available_time_hours": 8,
            "preferred_categories": ["freelance", "gig_economy"]
        }
        
        # Get daily ideas
        ideas = idea_engine.get_daily_ideas(user.id, user_profile)
        
        # Publish event
        await publish_event(
            EventType.IDEA_GENERATED,
            user.id,
            {"ideas_count": len(ideas.get("ideas", [])), "total_potential": ideas.get("total_potential", 0)},
            "idea_engine"
        )
        
        return {
            "status": "success",
            "ideas": ideas,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily ideas: {str(e)}")

@router.get("/income/{user_email}")
async def get_income_analysis(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get income stream analysis"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # This would integrate with IncomeStreamIntelligence
        # For now, return mock data
        analysis = {
            "status": "success",
            "income_streams": [
                {
                    "source": "Palkka",
                    "amount": 3200.0,
                    "reliability": "high",
                    "trend": "stable"
                },
                {
                    "source": "Freelance",
                    "amount": 500.0,
                    "reliability": "medium",
                    "trend": "growing"
                }
            ],
            "total_monthly_income": 3700.0,
            "recommendations": [
                "Harkitse lisätöitä viikonloppuisin",
                "Kehitä freelance-osaamistasi",
                "Sijoita osa tuloistasi"
            ]
        }
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze income: {str(e)}")

@router.get("/liabilities/{user_email}")
async def get_liabilities_analysis(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get liabilities and debt analysis"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # This would integrate with LiabilitiesInsight
        # For now, return mock data
        analysis = {
            "status": "success",
            "total_debt": 15000.0,
            "monthly_payments": 450.0,
            "interest_rate_avg": 8.5,
            "debt_types": [
                {
                    "type": "Asuntolaina",
                    "amount": 12000.0,
                    "interest_rate": 4.5,
                    "monthly_payment": 300.0
                },
                {
                    "type": "Kulutusluotto",
                    "amount": 3000.0,
                    "interest_rate": 15.0,
                    "monthly_payment": 150.0
                }
            ],
            "recommendations": [
                "Maksa ensin korkeakorkoiset velat",
                "Harkitse velkakonsolidointia",
                "Nosta säästöjä hätävaralle"
            ]
        }
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze liabilities: {str(e)}")

@router.get("/proactive/summary/{user_email}")
async def get_proactive_summary(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive proactive summary"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all AI insights
        ideas = idea_engine.get_daily_ideas(user.id, {})
        watchdog_status = watchdog_service.analyze_situation_room(user.id, db)
        learning_insights = learning_engine.get_learning_insights(user.id)
        
        summary = {
            "status": "success",
            "user_email": user_email,
            "timestamp": datetime.now().isoformat(),
            "insights": {
                "ideas": ideas,
                "watchdog": watchdog_status,
                "learning": learning_insights
            },
            "priority_actions": [
                "Tarkista budjettisi tällä viikolla",
                "Etsi lisätöitä viikonloppuisin",
                "Säästä vähintään 200€ tässä kuussa"
            ],
            "risk_level": "medium",
            "savings_progress": 18.5  # Percentage of 100k goal
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get proactive summary: {str(e)}")

@router.get("/watchdog/status/{user_email}")
async def get_watchdog_status(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get Sentinel Watchdog status"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get watchdog analysis
        analysis = watchdog_service.analyze_situation_room(user.id, db)
        
        # Publish event if there are alerts
        if analysis.get("risk_assessment", {}).get("risk_level") in ["high", "critical"]:
            await publish_event(
                EventType.WATCHDOG_ALERT,
                user.id,
                analysis,
                "watchdog_service",
                priority="high"
            )
        
        return {
            "status": "success",
            "watchdog_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get watchdog status: {str(e)}")

@router.get("/learning/insights/{user_email}")
async def get_learning_insights(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get Sentinel Learning Engine insights"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get learning insights
        insights = learning_engine.get_learning_insights(user.id)
        status = learning_engine.get_dynamic_status(user.id, db)
        
        # Publish event
        await publish_event(
            EventType.LEARNING_INSIGHT,
            user.id,
            {"insights": insights, "status": status},
            "learning_engine"
        )
        
        return {
            "status": "success",
            "learning_insights": insights,
            "user_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning insights: {str(e)}")

@router.get("/guardian/status/{user_email}")
async def get_guardian_status(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get Sentinel Guardian status"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # This would integrate with SentinelGuardianService
        # For now, return mock data
        guardian_status = {
            "status": "success",
            "goal_progress": 18.5,
            "current_savings": 18500.0,
            "target_amount": 100000.0,
            "monthly_savings": 1850.0,
            "alerts": [
                {
                    "level": "warning",
                    "title": "Säästötahti hidastunut",
                    "message": "Nykyisellä tahdilla tavoite kestää 7.2 vuotta"
                }
            ],
            "recommendations": [
                "Nosta kuukausisäästöjä 500€",
                "Etsi lisätuloja",
                "Optimoi kulut"
            ]
        }
        
        # Publish event if there are critical alerts
        if any(alert["level"] == "critical" for alert in guardian_status["alerts"]):
            await publish_event(
                EventType.GUARDIAN_WARNING,
                user.id,
                guardian_status,
                "guardian_service",
                priority="critical"
            )
        
        return guardian_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get guardian status: {str(e)}")

@router.post("/trigger/idea-generation")
async def trigger_idea_generation(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Manually trigger idea generation"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Trigger idea generation
        user_profile = {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "skills": ["Programming", "Design", "Writing"],
            "available_time_hours": 8,
            "preferred_categories": ["freelance", "gig_economy"]
        }
        
        ideas = idea_engine.get_daily_ideas(user.id, user_profile)
        
        return {
            "status": "success",
            "message": "Idea generation triggered successfully",
            "ideas": ideas,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger idea generation: {str(e)}")

@router.get("/system/health")
async def get_system_health() -> Dict[str, Any]:
    """Get AI system health status"""
    try:
        health_status = {
            "status": "healthy",
            "services": {
                "idea_engine": "active",
                "watchdog_service": "active",
                "learning_engine": "active",
                "event_bus": "active",
                "scheduler": "active"
            },
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}") 