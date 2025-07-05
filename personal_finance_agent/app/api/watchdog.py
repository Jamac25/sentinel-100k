"""
Watchdog API endpoints for real-time monitoring.
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from typing import Optional, Dict, Any
from datetime import datetime
import json
import logging

from app.db.init_db import get_db, SessionLocal
from app.services.sentinel_watchdog_service import SentinelWatchdogService
from app.services.event_bus import EventType, publish_event, event_bus
from app.models import User
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/watchdog", tags=["watchdog"])

# Initialize watchdog service
watchdog_service = SentinelWatchdogService()

# WebSocket connections
active_connections = []

@router.get("/status/{user_email}")
async def get_watchdog_status(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get real-time watchdog status"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get watchdog analysis
        analysis = watchdog_service.analyze_situation_room(user.id, db)
        
        # Get communication
        communication = watchdog_service.get_watchdog_communication(user.id, db)
        
        # Get survival suggestions
        suggestions = watchdog_service.generate_survival_suggestions(user.id, db)
        
        status = {
            "status": "success",
            "user_email": user_email,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "communication": communication,
            "suggestions": suggestions,
            "risk_level": analysis.get("risk_assessment", {}).get("risk_level", "unknown"),
            "watchdog_mode": analysis.get("risk_assessment", {}).get("watchdog_mode", "passive")
        }
        
        # Publish event if high risk
        if status["risk_level"] in ["high", "critical"]:
            await publish_event(
                EventType.WATCHDOG_ALERT,
                user.id,
                status,
                "watchdog_service",
                priority="high"
            )
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get watchdog status: {str(e)}")

@router.get("/alerts/{user_email}")
async def get_watchdog_alerts(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get active watchdog alerts"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get analysis
        analysis = watchdog_service.analyze_situation_room(user.id, db)
        
        # Generate alerts based on analysis
        alerts = []
        risk_level = analysis.get("risk_assessment", {}).get("risk_level", "low")
        
        if risk_level == "critical":
            alerts.append({
                "level": "critical",
                "title": "🚨 KRITTIINEN TILANNE!",
                "message": "100k€ tavoite on vaarassa! Toimia tarvitaan HETI!",
                "actions": [
                    "Etsi lisätöitä heti",
                    "Leikkaa kuluja radikaalisti",
                    "Harkitse velkakonsolidointia"
                ],
                "timestamp": datetime.now().isoformat()
            })
        elif risk_level == "high":
            alerts.append({
                "level": "high",
                "title": "⚠️ KORKEA RISKI",
                "message": "Säästötahti on liian hidas tavoitteen saavuttamiseksi",
                "actions": [
                    "Nosta säästöjä 300€/kk",
                    "Etsi lisätuloja",
                    "Optimoi kulut"
                ],
                "timestamp": datetime.now().isoformat()
            })
        elif risk_level == "moderate":
            alerts.append({
                "level": "moderate",
                "title": "📊 KESKITASOINEN RISKI",
                "message": "Säästöjä pitää nostaa hieman",
                "actions": [
                    "Nosta säästöjä 100€/kk",
                    "Tarkista tilaukset",
                    "Optimoi kulut"
                ],
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "status": "success",
            "alerts": alerts,
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.post("/emergency/{user_email}")
async def trigger_emergency_protocol(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Trigger emergency protocol"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get emergency protocol
        emergency = watchdog_service.get_emergency_protocol(user.id, db)
        
        # Publish critical event
        await publish_event(
            EventType.WATCHDOG_ALERT,
            user.id,
            {"emergency_protocol": emergency, "triggered_by": "manual"},
            "watchdog_service",
            priority="critical"
        )
        
        return {
            "status": "success",
            "emergency_protocol": emergency,
            "message": "Emergency protocol activated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger emergency: {str(e)}")

@router.get("/communication/{user_email}")
async def get_watchdog_communication(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get personalized watchdog communication"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get communication
        communication = watchdog_service.get_watchdog_communication(user.id, db)
        
        return {
            "status": "success",
            "communication": communication,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get communication: {str(e)}")

@router.get("/suggestions/{user_email}")
async def get_survival_suggestions(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get survival suggestions"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get suggestions
        suggestions = watchdog_service.generate_survival_suggestions(user.id, db)
        
        return {
            "status": "success",
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.websocket("/ws/{user_email}")
async def watchdog_websocket(websocket: WebSocket, user_email: str):
    """WebSocket for real-time watchdog updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial status
        db = SessionLocal()
        user = db.query(User).filter(User.email == user_email).first()
        
        if user:
            analysis = watchdog_service.analyze_situation_room(user.id, db)
            await websocket.send_text(json.dumps({
                "type": "status",
                "data": analysis,
                "timestamp": datetime.now().isoformat()
            }))
        
        # Keep connection alive and send updates
        while True:
            try:
                # Wait for any message from client
                data = await websocket.receive_text()
                
                # Send periodic updates
                if user:
                    analysis = watchdog_service.analyze_situation_room(user.id, db)
                    await websocket.send_text(json.dumps({
                        "type": "update",
                        "data": analysis,
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        db.close()

@router.get("/stats")
async def get_watchdog_stats() -> Dict[str, Any]:
    """Get watchdog statistics"""
    try:
        stats = {
            "active_connections": len(active_connections),
            "total_alerts": event_bus.get_stats().get("events_processed", 0),
            "high_priority_alerts": len([
                event for event in event_bus.get_event_history(EventType.WATCHDOG_ALERT)
                if event.priority in ["high", "critical"]
            ]),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/test-alert/{user_email}")
async def test_alert(
    user_email: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test alert system"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Publish test alert
        await publish_event(
            EventType.WATCHDOG_ALERT,
            user.id,
            {
                "test_alert": True,
                "message": "Tämä on testihälytys",
                "level": "info"
            },
            "watchdog_service",
            priority="normal"
        )
        
        return {
            "status": "success",
            "message": "Test alert sent successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test alert: {str(e)}") 