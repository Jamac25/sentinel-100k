"""
Event Bus Service - Palveluiden välinen kommunikaatio
Event-driven arkkitehtuuri Sentinel 100K:lle
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from app.db.init_db import SessionLocal

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types for Sentinel system"""
    # User events
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_PROFILE_UPDATED = "user_profile_updated"
    
    # Transaction events
    TRANSACTION_CREATED = "transaction_created"
    TRANSACTION_UPDATED = "transaction_updated"
    TRANSACTION_DELETED = "transaction_deleted"
    TRANSACTION_CATEGORIZED = "transaction_categorized"
    
    # Financial events
    BUDGET_EXCEEDED = "budget_exceeded"
    SAVINGS_GOAL_UPDATED = "savings_goal_updated"
    INCOME_DETECTED = "income_detected"
    EXPENSE_ANOMALY = "expense_anomaly"
    
    # AI Service events
    IDEA_GENERATED = "idea_generated"
    WATCHDOG_ALERT = "watchdog_alert"
    LEARNING_INSIGHT = "learning_insight"
    GUARDIAN_WARNING = "guardian_warning"
    
    # System events
    SCHEDULER_TASK_COMPLETED = "scheduler_task_completed"
    DOCUMENT_PROCESSED = "document_processed"
    MODEL_TRAINED = "model_trained"
    SYSTEM_HEALTH_CHECK = "system_health_check"

@dataclass
class Event:
    """Event data structure"""
    event_type: EventType
    user_id: Optional[int]
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    priority: str = "normal"  # low, normal, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "priority": self.priority
        }

class EventBus:
    """
    Event Bus for Sentinel 100K - Palveluiden välinen kommunikaatio
    
    Ominaisuudet:
    - Asynkroninen event processing
    - Prioriteettijärjestelmä
    - Event history ja replay
    - Service discovery
    - Error handling ja retry logic
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.is_running = False
        self.event_queue = asyncio.Queue()
        self.max_history_size = 10000
        
        # Service registry
        self.services = {}
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "events_failed": 0,
            "active_subscribers": 0
        }
    
    async def start(self):
        """Start event bus"""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self._process_events())
        logger.info("Event Bus started successfully")
    
    async def stop(self):
        """Stop event bus"""
        self.is_running = False
        logger.info("Event Bus stopped")
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        self.stats["active_subscribers"] = sum(len(callbacks) for callbacks in self.subscribers.values())
        logger.info(f"Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from event type"""
        if event_type in self.subscribers:
            if callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
                self.stats["active_subscribers"] = sum(len(callbacks) for callbacks in self.subscribers.values())
                logger.info(f"Unsubscribed from {event_type.value}")
    
    async def publish(self, event: Event):
        """Publish event to all subscribers"""
        try:
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)
            
            # Add to processing queue
            await self.event_queue.put(event)
            logger.debug(f"Published event: {event.event_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            self.stats["events_failed"] += 1
    
    async def _process_events(self):
        """Process events from queue"""
        while self.is_running:
            try:
                event = await self.event_queue.get()
                await self._handle_event(event)
                self.stats["events_processed"] += 1
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self.stats["events_failed"] += 1
    
    async def _handle_event(self, event: Event):
        """Handle individual event"""
        if event.event_type not in self.subscribers:
            return
        
        # Get subscribers for this event type
        callbacks = self.subscribers[event.event_type].copy()
        
        # Execute callbacks
        tasks = []
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(event))
                    tasks.append(task)
                else:
                    # Run sync callback in thread pool
                    loop = asyncio.get_event_loop()
                    task = loop.run_in_executor(None, callback, event)
                    tasks.append(task)
            except Exception as e:
                logger.error(f"Error executing callback for {event.event_type.value}: {e}")
        
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def register_service(self, service_name: str, service_instance: Any):
        """Register service for discovery"""
        self.services[service_name] = service_instance
        logger.info(f"Registered service: {service_name}")
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get registered service"""
        return self.services.get(service_name)
    
    def get_event_history(self, event_type: Optional[EventType] = None, 
                         user_id: Optional[int] = None, 
                         limit: int = 100) -> List[Event]:
        """Get event history with filters"""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        return events[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            **self.stats,
            "event_types": len(self.subscribers),
            "history_size": len(self.event_history),
            "queue_size": self.event_queue.qsize(),
            "is_running": self.is_running
        }

# Global event bus instance
event_bus = EventBus()

# Convenience functions
async def publish_event(event_type: EventType, user_id: Optional[int], 
                       data: Dict[str, Any], source: str, priority: str = "normal"):
    """Publish event to global event bus"""
    event = Event(
        event_type=event_type,
        user_id=user_id,
        data=data,
        timestamp=datetime.now(),
        source=source,
        priority=priority
    )
    await event_bus.publish(event)

def subscribe_to_event(event_type: EventType, callback: Callable):
    """Subscribe to event on global event bus"""
    event_bus.subscribe(event_type, callback)

def register_service(service_name: str, service_instance: Any):
    """Register service on global event bus"""
    event_bus.register_service(service_name, service_instance) 