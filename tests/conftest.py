"""
Pytest configuration and fixtures for Sentinel 100K tests.
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your application components
try:
    from personal_finance_agent.app.main import app
    from personal_finance_agent.app.db.base import Base
    from personal_finance_agent.app.core.config import get_settings
    from personal_finance_agent.app.models.user import User
    from personal_finance_agent.app.models.transaction import Transaction
    from personal_finance_agent.app.models.category import Category
    from personal_finance_agent.app.models.goal import Goal
    from personal_finance_agent.app.models.budget import Budget
except ImportError:
    # Fallback if modules are not available
    app = None
    Base = None
    get_settings = None
    User = None
    Transaction = None
    Category = None
    Goal = None
    Budget = None

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    if Base:
        Base.metadata.create_all(bind=engine)
    yield engine

@pytest.fixture(scope="function")
def db_session(engine):
    """Create a database session for each test."""
    if not engine:
        pytest.skip("Database not available")
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Start a transaction
    transaction = session.begin()
    
    yield session
    
    # Rollback the transaction
    transaction.rollback()
    session.close()

@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create test client with database session override."""
    if not app:
        pytest.skip("FastAPI app not available")
    
    def override_get_db():
        yield db_session
    
    # Override the dependency
    app.dependency_overrides[get_settings] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()

@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls for testing."""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock chat completions
        mock_instance.chat.completions.create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Test AI response",
                        role="assistant"
                    )
                )
            ]
        )
        
        yield mock_instance

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": "hashed_password_123",
        "monthly_income": 3000.0,
        "savings_goal": 100000.0,
        "current_savings": 25000.0,
        "is_active": True,
        "risk_tolerance": "moderate",
        "financial_goals": ["house", "retirement"],
        "employment_status": "employed",
        "age_range": "25-35",
        "location": "Helsinki",
        "language_preference": "fi"
    }

@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "amount": 150.50,
        "description": "Grocery shopping",
        "transaction_date": "2024-01-15",
        "is_income": False,
        "category": "Ruoka",
        "subcategory": "Päivittäistarvikkeet",
        "payment_method": "card",
        "location": "K-Market",
        "notes": "Weekly groceries"
    }

@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "name": "Ruoka",
        "is_income": False,
        "is_essential": True,
        "budget_percentage": 25.0,
        "keywords": ["ruoka", "market", "grocery", "leipomo"],
        "description": "Food and groceries",
        "icon": "🍔",
        "color": "#FF6B6B"
    }

@pytest.fixture
def sample_goal_data():
    """Sample goal data for testing."""
    return {
        "title": "Emergency Fund",
        "description": "Build 6 months of expenses as emergency fund",
        "target_amount": 15000.0,
        "current_amount": 5000.0,
        "target_date": "2024-12-31",
        "goal_type": "savings",
        "priority": "high",
        "category": "Emergency",
        "is_active": True
    }

@pytest.fixture
def sample_budget_data():
    """Sample budget data for testing."""
    return {
        "category": "Ruoka",
        "amount": 800.0,
        "period": "monthly",
        "spent_amount": 245.80,
        "alert_threshold": 80.0,
        "rollover_unused": True,
        "notes": "Monthly food budget"
    }

@pytest.fixture
def authenticated_headers():
    """Sample authentication headers for API testing."""
    return {
        "Authorization": "Bearer test_token_123",
        "Content-Type": "application/json"
    }

@pytest.fixture
def mock_ai_services():
    """Mock all AI services for testing."""
    with patch.multiple(
        'personal_finance_agent.app.services',
        idea_engine=Mock(),
        sentinel_watchdog_service=Mock(),
        sentinel_learning_engine=Mock(),
        income_stream_intelligence=Mock(),
        liabilities_insight=Mock(),
        sentinel_guardian_service=Mock(),
        user_context_service=Mock(),
        scheduler_service=Mock(),
    ) as mocks:
        yield mocks

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit for testing frontend components."""
    with patch('streamlit.write') as mock_write, \
         patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.columns') as mock_columns:
        yield {
            'write': mock_write,
            'sidebar': mock_sidebar,
            'columns': mock_columns
        }

# Test markers
pytestmark = pytest.mark.asyncio

# Test configuration
pytest_plugins = [
    "pytest_asyncio",
    "pytest_cov",
]

# Custom test markers
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "ai: mark test as requiring AI/OpenAI API"
    )
    config.addinivalue_line(
        "markers", "db: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API endpoint test"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers."""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ["integration", "slow", "ai", "db", "api"] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if "test_full_" in item.name or "test_integration_" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add ai marker to tests that use AI services
        if "ai_" in item.name or "openai" in item.name:
            item.add_marker(pytest.mark.ai)
        
        # Add db marker to tests that use database
        if "db_" in item.name or "database" in item.name:
            item.add_marker(pytest.mark.db)
        
        # Add api marker to tests that test API endpoints
        if "api_" in item.name or "endpoint" in item.name:
            item.add_marker(pytest.mark.api) 