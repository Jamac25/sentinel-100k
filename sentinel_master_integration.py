#!/usr/bin/env python3
"""
🚀 SENTINEL 100K - MASTER INTEGRATION SERVICE
============================================
Yhdistää kaikki 8 ominaisuutta 100% integraatiolla
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import aioredis
from fastapi import FastAPI, WebSocket
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel

# Import all services (assuming they exist in the project)
from personal_finance_agent.app.services.idea_engine import IdeaEngine
from personal_finance_agent.app.services.sentinel_watchdog_service import SentinelWatchdogService
from personal_finance_agent.app.services.sentinel_learning_engine import SentinelLearningEngine
from personal_finance_agent.app.services.income_stream_intelligence import IncomeStreamIntelligence
from personal_finance_agent.app.services.liabilities_insight import LiabilitiesInsight
from personal_finance_agent.app.services.categorization_service import TransactionCategorizationService
from personal_finance_agent.app.services.ocr_service import OCREngine

# Event types for cross-service communication
class EventType:
    NEW_TRANSACTION = "new_transaction"
    GOAL_UPDATE = "goal_update"
    RISK_ALERT = "risk_alert"
    IDEA_GENERATED = "idea_generated"
    PROFILE_UPDATED = "profile_updated"
    BUDGET_EXCEEDED = "budget_exceeded"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"

class ServiceEvent(BaseModel):
    type: str
    source: str
    target: Optional[str] = None  # None = broadcast to all
    data: Dict[str, Any]
    timestamp: datetime = datetime.now()

class MasterIntegrationService:
    """
    Keskitetty palvelu joka yhdistää kaikki Sentinel 100K:n ominaisuudet
    """
    
    def __init__(self):
        # Initialize all services
        self.services = {
            'dashboard': self.init_dashboard(),
            'budget': self.init_budget_system(),
            'goals': self.init_goal_tracking(),
            'onboarding': self.init_onboarding(),
            'ideas': IdeaEngine(),
            'watchdog': SentinelWatchdogService(),
            'learning': SentinelLearningEngine(),
            'chat': self.init_ai_chat()
        }
        
        # Event bus for cross-service communication
        self.event_bus = asyncio.Queue()
        self.redis = None  # For pub/sub
        
        # Scheduler for automated tasks
        self.scheduler = AsyncIOScheduler()
        
        # Service status tracking
        self.service_health = {name: True for name in self.services}
        
        # WebSocket connections for real-time updates
        self.active_connections: List[WebSocket] = []
        
    async def initialize(self):
        """Initialize all connections and services"""
        # Connect to Redis for pub/sub
        self.redis = await aioredis.create_redis_pool('redis://localhost')
        
        # Start event processor
        asyncio.create_task(self.process_events())
        
        # Setup automated triggers
        self.setup_automated_triggers()
        
        # Start scheduler
        self.scheduler.start()
        
        print("✅ Master Integration Service initialized")
        
    def setup_automated_triggers(self):
        """Configure all automated triggers"""
        
        # 1. Daily triggers (6 AM)
        self.scheduler.add_job(
            self.daily_morning_routine,
            'cron',
            hour=6,
            minute=0,
            id='daily_morning'
        )
        
        # 2. Real-time monitoring (every 30 seconds)
        self.scheduler.add_job(
            self.realtime_monitoring,
            'interval',
            seconds=30,
            id='realtime_monitor'
        )
        
        # 3. Weekly analysis (Monday midnight)
        self.scheduler.add_job(
            self.weekly_analysis,
            'cron',
            day_of_week='mon',
            hour=0,
            minute=0,
            id='weekly_analysis'
        )
        
        # 4. Night analysis (2 AM)
        self.scheduler.add_job(
            self.night_analysis,
            'cron',
            hour=2,
            minute=0,
            id='night_analysis'
        )
        
    async def daily_morning_routine(self):
        """Päivittäinen aamurutiini - kaikki palvelut"""
        print("🌅 Starting daily morning routine...")
        
        users = await self.get_all_active_users()
        
        for user in users:
            try:
                # 1. Generate daily ideas (IdeaEngine)
                ideas = await self.services['ideas'].get_daily_ideas(
                    user['id'], 
                    user['profile']
                )
                
                # 2. Check financial health (Watchdog)
                risk_assessment = await self.services['watchdog'].analyze_situation(
                    user['id'],
                    None  # Mock DB session
                )
                
                # 3. Update learning profile
                await self.services['learning'].update_user_profile(
                    user['id'],
                    {'last_active': datetime.now()}
                )
                
                # 4. Update dashboard with fresh data
                await self.publish_event(ServiceEvent(
                    type=EventType.PROFILE_UPDATED,
                    source='morning_routine',
                    data={
                        'user_id': user['id'],
                        'ideas': ideas,
                        'risk_assessment': risk_assessment,
                        'timestamp': datetime.now().isoformat()
                    }
                ))
                
            except Exception as e:
                print(f"Error in morning routine for user {user['id']}: {e}")
                
    async def realtime_monitoring(self):
        """Reaaliaikainen valvonta kaikille käyttäjille"""
        users = await self.get_all_active_users()
        
        for user in users:
            # Check if any service needs immediate attention
            watchdog_status = await self.services['watchdog'].get_current_mode(user['id'])
            
            if watchdog_status == 'emergency':
                # Trigger emergency protocol
                await self.trigger_emergency_protocol(user['id'])
                
    async def process_events(self):
        """Process cross-service events"""
        while True:
            try:
                event = await self.event_bus.get()
                await self.route_event(event)
            except Exception as e:
                print(f"Error processing event: {e}")
                
    async def route_event(self, event: ServiceEvent):
        """Route events to appropriate services"""
        
        # Log event
        print(f"📨 Event: {event.type} from {event.source}")
        
        # Handle specific event types
        if event.type == EventType.NEW_TRANSACTION:
            await self.handle_new_transaction(event.data)
            
        elif event.type == EventType.GOAL_UPDATE:
            await self.handle_goal_update(event.data)
            
        elif event.type == EventType.RISK_ALERT:
            await self.handle_risk_alert(event.data)
            
        elif event.type == EventType.IDEA_GENERATED:
            await self.handle_new_idea(event.data)
            
        # Broadcast to WebSocket clients
        await self.broadcast_to_clients(event)
        
    async def handle_new_transaction(self, data: dict):
        """Handle new transaction across all services"""
        
        # 1. Update budget
        budget_impact = await self.services['budget'].process_transaction(data)
        
        # 2. Check watchdog
        risk_check = await self.services['watchdog'].check_transaction_risk(data)
        
        # 3. Update goals
        goal_impact = await self.services['goals'].update_from_transaction(data)
        
        # 4. Learning engine learns
        await self.services['learning'].learn_from_transaction(data)
        
        # 5. Maybe generate ideas if needed
        if budget_impact.get('needs_extra_income'):
            ideas = await self.services['ideas'].generate_emergency_ideas(
                data['user_id']
            )
            
        # 6. Update dashboard
        await self.update_dashboard_metrics(data['user_id'])
        
    async def handle_risk_alert(self, data: dict):
        """Handle risk alerts from watchdog"""
        
        user_id = data['user_id']
        risk_level = data['risk_level']
        
        # 1. Get recommendations from AI
        recommendations = await self.services['chat'].get_risk_recommendations(
            user_id, 
            risk_level
        )
        
        # 2. Adjust budget if needed
        if risk_level >= 0.8:
            await self.services['budget'].activate_emergency_mode(user_id)
            
        # 3. Generate recovery ideas
        recovery_ideas = await self.services['ideas'].generate_recovery_plan(
            user_id
        )
        
        # 4. Notify user
        await self.send_notification(user_id, {
            'type': 'risk_alert',
            'level': risk_level,
            'recommendations': recommendations,
            'recovery_ideas': recovery_ideas
        })
        
    async def cross_service_intelligence(self, user_id: str) -> dict:
        """Get combined intelligence from all services"""
        
        # Gather data from all services in parallel
        tasks = [
            self.services['ideas'].get_current_ideas(user_id),
            self.services['watchdog'].get_risk_summary(user_id),
            self.services['learning'].get_predictions(user_id),
            self.services['budget'].get_status(user_id),
            self.services['goals'].get_progress(user_id)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine into unified intelligence
        combined = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'ideas': results[0] if not isinstance(results[0], Exception) else None,
            'risk_assessment': results[1] if not isinstance(results[1], Exception) else None,
            'predictions': results[2] if not isinstance(results[2], Exception) else None,
            'budget_status': results[3] if not isinstance(results[3], Exception) else None,
            'goal_progress': results[4] if not isinstance(results[4], Exception) else None,
            'health_score': self.calculate_overall_health(results)
        }
        
        return combined
        
    def calculate_overall_health(self, service_results: list) -> float:
        """Calculate overall financial health score"""
        
        valid_results = [r for r in service_results if not isinstance(r, Exception)]
        
        if not valid_results:
            return 0.0
            
        # Weight different factors
        scores = []
        
        for result in valid_results:
            if isinstance(result, dict):
                if 'health_score' in result:
                    scores.append(result['health_score'])
                elif 'progress' in result:
                    scores.append(result['progress'] / 100)
                elif 'risk_level' in result:
                    scores.append(1 - result['risk_level'])
                    
        return sum(scores) / len(scores) if scores else 0.5
        
    # Helper methods
    
    def init_dashboard(self):
        """Initialize enhanced dashboard service"""
        return {
            'get_metrics': self.get_dashboard_metrics,
            'update': self.update_dashboard_metrics
        }
        
    def init_budget_system(self):
        """Initialize enhanced budget system"""
        return {
            'process_transaction': self.process_budget_transaction,
            'get_status': self.get_budget_status,
            'activate_emergency_mode': self.activate_budget_emergency
        }
        
    def init_goal_tracking(self):
        """Initialize smart goal tracking"""
        return {
            'update_from_transaction': self.update_goal_from_transaction,
            'get_progress': self.get_goal_progress,
            'adjust_dynamically': self.adjust_goals_dynamically
        }
        
    def init_onboarding(self):
        """Initialize deep onboarding system"""
        return {
            'analyze_cv': self.analyze_cv_with_ai,
            'create_profile': self.create_user_profile
        }
        
    def init_ai_chat(self):
        """Initialize fully integrated AI chat"""
        return {
            'process_message': self.process_chat_message,
            'get_risk_recommendations': self.get_ai_recommendations
        }
        
    async def publish_event(self, event: ServiceEvent):
        """Publish event to event bus"""
        await self.event_bus.put(event)
        
        # Also publish to Redis for external services
        if self.redis:
            await self.redis.publish(
                f'sentinel:events:{event.type}',
                json.dumps(event.dict())
            )
            
    async def broadcast_to_clients(self, event: ServiceEvent):
        """Broadcast event to all connected WebSocket clients"""
        message = json.dumps({
            'type': 'service_event',
            'event': event.dict()
        })
        
        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
                
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)
            
    async def get_all_active_users(self) -> List[dict]:
        """Get all active users from database"""
        # This would query the actual database
        # For now, return mock data
        return [
            {
                'id': 'user1',
                'profile': {
                    'email': 'demo@example.com',
                    'skills': ['programming', 'design'],
                    'monthly_income': 3200
                }
            }
        ]
        
    # Placeholder methods for service functions
    
    async def get_dashboard_metrics(self, user_id: str) -> dict:
        return await self.cross_service_intelligence(user_id)
        
    async def update_dashboard_metrics(self, user_id: str):
        metrics = await self.get_dashboard_metrics(user_id)
        await self.publish_event(ServiceEvent(
            type=EventType.PROFILE_UPDATED,
            source='dashboard',
            data={'user_id': user_id, 'metrics': metrics}
        ))
        
    async def process_budget_transaction(self, data: dict) -> dict:
        # Process transaction in budget system
        return {'needs_extra_income': data.get('amount', 0) > 500}
        
    async def get_budget_status(self, user_id: str) -> dict:
        return {'health_score': 0.75, 'remaining_budget': 1200}
        
    async def activate_budget_emergency(self, user_id: str):
        print(f"🚨 Emergency budget mode activated for {user_id}")
        
    async def update_goal_from_transaction(self, data: dict) -> dict:
        return {'progress': 0.35, 'on_track': True}
        
    async def get_goal_progress(self, user_id: str) -> dict:
        return {'progress': 35.0, 'days_remaining': 180}
        
    async def adjust_goals_dynamically(self, user_id: str):
        print(f"📊 Adjusting goals for {user_id}")
        
    async def analyze_cv_with_ai(self, cv_file: bytes) -> dict:
        return {'skills': ['python', 'react'], 'experience_years': 5}
        
    async def create_user_profile(self, data: dict) -> dict:
        return {'profile_id': 'new_profile_123', 'status': 'created'}
        
    async def process_chat_message(self, user_id: str, message: str) -> str:
        return f"AI response to: {message}"
        
    async def get_ai_recommendations(self, user_id: str, risk_level: float) -> list:
        return ["Reduce spending", "Find additional income", "Review budget"]
        
    async def send_notification(self, user_id: str, notification: dict):
        print(f"📱 Notification sent to {user_id}: {notification}")
        
    async def trigger_emergency_protocol(self, user_id: str):
        print(f"🚨 EMERGENCY PROTOCOL ACTIVATED for {user_id}")
        
        # 1. Freeze non-essential spending
        await self.services['budget'].activate_emergency_mode(user_id)
        
        # 2. Generate emergency income ideas
        ideas = await self.services['ideas'].generate_emergency_ideas(user_id)
        
        # 3. Alert user
        await self.send_notification(user_id, {
            'type': 'emergency',
            'message': 'Emergency financial protocol activated',
            'ideas': ideas
        })


# FastAPI app for the integration service
app = FastAPI(title="Sentinel Master Integration Service")

# Global instance
master = MasterIntegrationService()

@app.on_event("startup")
async def startup():
    await master.initialize()
    
@app.get("/api/v1/integration/status")
async def get_integration_status():
    """Get status of all integrated services"""
    return {
        'services': master.service_health,
        'event_queue_size': master.event_bus.qsize(),
        'active_connections': len(master.active_connections),
        'scheduler_jobs': [job.id for job in master.scheduler.get_jobs()]
    }
    
@app.get("/api/v1/integration/intelligence/{user_id}")
async def get_cross_service_intelligence(user_id: str):
    """Get combined intelligence from all services"""
    return await master.cross_service_intelligence(user_id)
    
@app.post("/api/v1/integration/event")
async def publish_event(event: ServiceEvent):
    """Publish an event to the integration service"""
    await master.publish_event(event)
    return {"status": "event_published"}
    
@app.websocket("/ws/integration")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time integration updates"""
    await websocket.accept()
    master.active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        master.active_connections.remove(websocket)
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200) 