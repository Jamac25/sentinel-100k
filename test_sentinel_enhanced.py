#!/usr/bin/env python3
"""
🧪 SENTINEL 100K - ENHANCED UNIT TESTS
=====================================
Comprehensive test suite for all Sentinel features with pytest.

Tests cover:
- Data validation
- Event bus functionality
- AI services
- Caching system
- Error handling
- API endpoints
- Authentication
- Business logic

Run with: pytest test_sentinel_enhanced.py -v
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the main application
import sys
sys.path.append('.')
from sentinel_render_enhanced import (
    SentinelEventBus, SentinelContext, SentinelCache,
    EnhancedIdeaEngine, EnhancedWatchdog, EnhancedLearningEngine,
    EventType, SentinelEvent, UserLogin, UserRegister, 
    DeepOnboardingData, TransactionData, BudgetData,
    load_data, save_data
)

# 🧪 TEST FIXTURES
@pytest.fixture
def event_bus():
    """Create a fresh event bus for each test."""
    return SentinelEventBus()

@pytest.fixture
def context_system(event_bus):
    """Create a fresh context system for each test."""
    return SentinelContext(event_bus)

@pytest.fixture
def cache():
    """Create a fresh cache for each test."""
    return SentinelCache()

@pytest.fixture
def temp_data_file():
    """Create a temporary data file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"test": "data"}, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)

# 🧪 EVENT BUS TESTS
class TestEventBus:
    """Test the event bus functionality."""
    
    def test_event_bus_initialization(self, event_bus):
        """Test event bus initialization."""
        assert event_bus.subscribers is not None
        assert event_bus.event_history == []
        assert event_bus.active_triggers == {}
        
        # Check all event types are registered
        for event_type in EventType:
            assert event_type in event_bus.subscribers
            assert isinstance(event_bus.subscribers[event_type], list)
    
    def test_event_subscription(self, event_bus):
        """Test event subscription."""
        callback = Mock()
        event_bus.subscribe(EventType.USER_LOGIN, callback)
        
        assert callback in event_bus.subscribers[EventType.USER_LOGIN]
        assert len(event_bus.subscribers[EventType.USER_LOGIN]) == 1
    
    def test_event_publishing(self, event_bus):
        """Test event publishing."""
        callback = Mock()
        event_bus.subscribe(EventType.NEW_TRANSACTION, callback)
        
        event = SentinelEvent(
            event_type=EventType.NEW_TRANSACTION,
            user_id="test@example.com",
            data={"amount": 100},
            timestamp=datetime.now(),
            source="test"
        )
        
        event_bus.publish(event)
        
        assert len(event_bus.event_history) == 1
        assert event_bus.event_history[0] == event
        callback.assert_called_once_with(event)
    
    def test_get_recent_events(self, event_bus):
        """Test getting recent events for a user."""
        user_id = "test@example.com"
        
        # Create multiple events
        for i in range(5):
            event = SentinelEvent(
                event_type=EventType.NEW_TRANSACTION,
                user_id=user_id,
                data={"amount": i * 10},
                timestamp=datetime.now(),
                source="test"
            )
            event_bus.publish(event)
        
        # Create event for different user
        other_event = SentinelEvent(
            event_type=EventType.NEW_TRANSACTION,
            user_id="other@example.com",
            data={"amount": 999},
            timestamp=datetime.now(),
            source="test"
        )
        event_bus.publish(other_event)
        
        recent_events = event_bus.get_recent_events(user_id, limit=3)
        
        assert len(recent_events) == 3
        assert all(event.user_id == user_id for event in recent_events)

# 🧪 CONTEXT SYSTEM TESTS
class TestContextSystem:
    """Test the context system functionality."""
    
    def test_context_initialization(self, context_system):
        """Test context system initialization."""
        assert context_system.event_bus is not None
        assert context_system.user_contexts == {}
    
    def test_get_user_context_creation(self, context_system):
        """Test user context creation."""
        user_email = "test@example.com"
        context = context_system.get_user_context(user_email)
        
        assert context is not None
        assert "profile" in context
        assert "current_cycle" in context
        assert "budget_status" in context
        assert "watchdog_mode" in context
        assert "recent_events" in context
        assert "ai_insights" in context
        assert "last_updated" in context
    
    def test_context_update(self, context_system):
        """Test context updates."""
        user_email = "test@example.com"
        updates = {"watchdog_mode": "aggressive", "new_field": "value"}
        
        context_system.update_context(user_email, updates)
        context = context_system.get_user_context(user_email)
        
        assert context["watchdog_mode"] == "aggressive"
        assert context["new_field"] == "value"
        assert "last_updated" in context

# 🧪 CACHE SYSTEM TESTS
class TestCacheSystem:
    """Test the cache system functionality."""
    
    def test_cache_initialization(self, cache):
        """Test cache initialization."""
        assert cache.cache == {}
        assert cache.ttl == {}
        assert "hits" in cache.stats
        assert "misses" in cache.stats
        assert "sets" in cache.stats
        assert "deletes" in cache.stats
    
    def test_cache_set_get(self, cache):
        """Test basic cache set and get operations."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Set value
        result = cache.set(key, value, ttl_seconds=60)
        assert result is True
        
        # Get value
        retrieved = cache.get(key)
        assert retrieved == value
        
        # Check stats
        assert cache.stats["sets"] == 1
        assert cache.stats["hits"] == 1
        assert cache.stats["misses"] == 0
    
    def test_cache_miss(self, cache):
        """Test cache miss behavior."""
        retrieved = cache.get("nonexistent_key")
        assert retrieved is None
        assert cache.stats["misses"] == 1
        assert cache.stats["hits"] == 0
    
    def test_cache_delete(self, cache):
        """Test cache delete operation."""
        key = "test_key"
        value = "test_value"
        
        cache.set(key, value)
        assert cache.get(key) == value
        
        cache.delete(key)
        assert cache.get(key) is None
        assert cache.stats["deletes"] == 1
    
    def test_cache_clear(self, cache):
        """Test cache clear operation."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.cache) == 2
        
        cache.clear()
        assert len(cache.cache) == 0
        assert len(cache.ttl) == 0
    
    def test_cache_stats(self, cache):
        """Test cache statistics."""
        # Add some data
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # Hit
        cache.get("key2")  # Hit
        cache.get("nonexistent")  # Miss
        cache.delete("key1")
        
        stats = cache.get_stats()
        
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["sets"] == 2
        assert stats["deletes"] == 1
        assert stats["current_size"] == 1
        assert "hit_rate" in stats

# 🧪 DATA VALIDATION TESTS
class TestDataValidation:
    """Test data validation with Pydantic models."""
    
    def test_valid_user_login(self):
        """Test valid user login data."""
        data = {
            "email": "test@example.com",
            "password": "securepassword123"
        }
        
        user_login = UserLogin(**data)
        assert user_login.email == "test@example.com"
        assert user_login.password == "securepassword123"
    
    def test_invalid_email_format(self):
        """Test invalid email format."""
        data = {
            "email": "invalid-email",
            "password": "securepassword123"
        }
        
        with pytest.raises(ValueError):
            UserLogin(**data)
    
    def test_short_password(self):
        """Test password too short."""
        data = {
            "email": "test@example.com",
            "password": "123"
        }
        
        with pytest.raises(ValueError):
            UserLogin(**data)
    
    def test_valid_user_register(self):
        """Test valid user registration data."""
        data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "securepassword123"
        }
        
        user_register = UserRegister(**data)
        assert user_register.email == "test@example.com"
        assert user_register.name == "Test User"
        assert user_register.password == "securepassword123"
    
    def test_valid_deep_onboarding(self):
        """Test valid deep onboarding data."""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "profession": "Software Developer",
            "current_savings": 5000.0,
            "savings_goal": 10000.0,
            "monthly_income": 4000.0,
            "monthly_expenses": 2500.0,
            "skills": ["Python", "JavaScript"],
            "work_experience_years": 3,
            "education_level": "bachelor",
            "risk_tolerance": "medium",
            "time_availability_hours": 20,
            "financial_goals": ["Emergency fund", "Investment"],
            "debt_amount": 0.0,
            "investment_experience": "beginner",
            "preferred_income_methods": ["Freelancing", "Side projects"]
        }
        
        onboarding = DeepOnboardingData(**data)
        assert onboarding.name == "Test User"
        assert onboarding.age == 25
        assert onboarding.savings_goal == 10000.0
    
    def test_invalid_savings_goal(self):
        """Test savings goal validation."""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "profession": "Software Developer",
            "current_savings": 10000.0,  # Higher than goal
            "savings_goal": 5000.0,      # Lower than current
            "monthly_income": 4000.0,
            "monthly_expenses": 2500.0,
            "skills": ["Python"],
            "work_experience_years": 3,
            "education_level": "bachelor",
            "risk_tolerance": "medium",
            "time_availability_hours": 20,
            "financial_goals": ["Emergency fund"],
            "debt_amount": 0.0,
            "investment_experience": "beginner",
            "preferred_income_methods": ["Freelancing"]
        }
        
        with pytest.raises(ValueError, match="Savings goal must be greater than current savings"):
            DeepOnboardingData(**data)
    
    def test_invalid_monthly_expenses(self):
        """Test monthly expenses validation."""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "profession": "Software Developer",
            "current_savings": 5000.0,
            "savings_goal": 10000.0,
            "monthly_income": 2000.0,     # Lower than expenses
            "monthly_expenses": 3000.0,   # Higher than income
            "skills": ["Python"],
            "work_experience_years": 3,
            "education_level": "bachelor",
            "risk_tolerance": "medium",
            "time_availability_hours": 20,
            "financial_goals": ["Emergency fund"],
            "debt_amount": 0.0,
            "investment_experience": "beginner",
            "preferred_income_methods": ["Freelancing"]
        }
        
        with pytest.raises(ValueError, match="Monthly expenses cannot exceed monthly income"):
            DeepOnboardingData(**data)

# 🧪 UTILITY FUNCTION TESTS
class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_load_data_existing_file(self, temp_data_file):
        """Test loading data from existing file."""
        data = load_data(temp_data_file)
        assert data == {"test": "data"}
    
    def test_load_data_nonexistent_file(self):
        """Test loading data from nonexistent file."""
        data = load_data("nonexistent_file.json")
        assert data == {}
    
    def test_save_data(self, temp_data_file):
        """Test saving data to file."""
        test_data = {"new": "data", "number": 42}
        save_data(temp_data_file, test_data)
        
        # Verify data was saved
        with open(temp_data_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data == test_data

# 🧪 AI SERVICES TESTS
class TestAIServices:
    """Test AI services functionality."""
    
    def test_enhanced_idea_engine_initialization(self, event_bus, context_system):
        """Test enhanced idea engine initialization."""
        idea_engine = EnhancedIdeaEngine(event_bus, context_system)
        
        assert idea_engine.event_bus == event_bus
        assert idea_engine.context == context_system
        assert len(idea_engine.daily_themes) == 7
    
    def test_idea_engine_daily_ideas(self, event_bus, context_system):
        """Test daily ideas generation."""
        idea_engine = EnhancedIdeaEngine(event_bus, context_system)
        user_email = "test@example.com"
        
        result = idea_engine.get_daily_ideas(user_email)
        
        assert result["status"] == "success"
        assert "ideas" in result
        assert "daily_theme" in result
        assert "total_potential_earning" in result
        assert result["personalized"] is True
        assert result["context_aware"] is True
        assert result["automation_active"] is True
    
    def test_emergency_ideas_generation(self, event_bus, context_system):
        """Test emergency ideas generation."""
        idea_engine = EnhancedIdeaEngine(event_bus, context_system)
        user_email = "test@example.com"
        excess_amount = 500.0
        
        ideas = idea_engine.generate_emergency_ideas(user_email, excess_amount)
        
        assert isinstance(ideas, list)
        assert len(ideas) > 0
        assert all("title" in idea for idea in ideas)
        assert all("estimated_earning" in idea for idea in ideas)
        assert all("priority" in idea for idea in ideas)

# 🧪 INTEGRATION TESTS
class TestIntegration:
    """Test integration between components."""
    
    def test_event_bus_with_context_system(self, event_bus, context_system):
        """Test event bus integration with context system."""
        user_email = "test@example.com"
        
        # Update context
        context_system.update_context(user_email, {"watchdog_mode": "aggressive"})
        
        # Check that event was published
        events = event_bus.get_recent_events(user_email)
        assert len(events) > 0
        
        # Check event type
        assert events[-1].event_type == EventType.LEARNING_UPDATE
    
    def test_cache_with_ai_services(self, cache, event_bus, context_system):
        """Test cache integration with AI services."""
        idea_engine = EnhancedIdeaEngine(event_bus, context_system)
        user_email = "test@example.com"
        
        # Cache some ideas
        cache_key = f"ideas_{user_email}"
        ideas_data = idea_engine.get_daily_ideas(user_email)
        cache.set(cache_key, ideas_data, ttl_seconds=300)
        
        # Retrieve from cache
        cached_ideas = cache.get(cache_key)
        assert cached_ideas == ideas_data
        
        # Check cache stats
        stats = cache.get_stats()
        assert stats["sets"] == 1
        assert stats["hits"] == 1

# 🧪 ERROR HANDLING TESTS
class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_event_bus_callback_error(self, event_bus):
        """Test event bus handles callback errors gracefully."""
        def failing_callback(event):
            raise Exception("Callback error")
        
        event_bus.subscribe(EventType.NEW_TRANSACTION, failing_callback)
        
        event = SentinelEvent(
            event_type=EventType.NEW_TRANSACTION,
            user_id="test@example.com",
            data={},
            timestamp=datetime.now(),
            source="test"
        )
        
        # Should not raise exception
        event_bus.publish(event)
        
        # Event should still be in history
        assert len(event_bus.event_history) == 1
    
    def test_cache_error_handling(self, cache):
        """Test cache error handling."""
        # Test with invalid key type
        result = cache.set(None, "value")
        assert result is False
        
        # Test get with invalid key
        result = cache.get(None)
        assert result is None

# 🧪 PERFORMANCE TESTS
class TestPerformance:
    """Test performance characteristics."""
    
    def test_cache_performance(self, cache):
        """Test cache performance with many operations."""
        import time
        
        # Measure set performance
        start_time = time.time()
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        set_time = time.time() - start_time
        
        # Measure get performance
        start_time = time.time()
        for i in range(1000):
            cache.get(f"key_{i}")
        get_time = time.time() - start_time
        
        # Should be fast (less than 1 second for 1000 operations)
        assert set_time < 1.0
        assert get_time < 1.0
    
    def test_event_bus_performance(self, event_bus):
        """Test event bus performance with many events."""
        import time
        
        callback = Mock()
        event_bus.subscribe(EventType.NEW_TRANSACTION, callback)
        
        start_time = time.time()
        for i in range(1000):
            event = SentinelEvent(
                event_type=EventType.NEW_TRANSACTION,
                user_id=f"user_{i}@example.com",
                data={"amount": i},
                timestamp=datetime.now(),
                source="test"
            )
            event_bus.publish(event)
        publish_time = time.time() - start_time
        
        # Should be fast
        assert publish_time < 1.0
        assert callback.call_count == 1000

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"]) 