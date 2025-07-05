"""
Database initialization and session management.
"""
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
if settings.database_url.startswith("sqlite"):
    # SQLite for development
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=settings.debug
    )
else:
    # PostgreSQL for production
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.debug
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def init_db():
    """Initialize database tables."""
    try:
        # Import all models to ensure they are registered
        from app.models import (
            User, Transaction, Category, Document, 
            Budget, Goal, Recommendation, AgentState, CategoryCorrection
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize default categories if they don't exist
        _init_default_categories()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def _init_default_categories():
    """Initialize default transaction categories."""
    db = SessionLocal()
    try:
        # Check if categories already exist
        existing_categories = db.query(Category).count()
        if existing_categories > 0:
            logger.info("Categories already exist, skipping initialization")
            return
        
        # Default Finnish categories
        default_categories = [
            {"name": "Ruoka ja juoma", "color": "#FF6B6B", "icon": "🍽️"},
            {"name": "Liikenne", "color": "#4ECDC4", "icon": "🚗"},
            {"name": "Asuminen", "color": "#45B7D1", "icon": "🏠"},
            {"name": "Viihde", "color": "#96CEB4", "icon": "🎬"},
            {"name": "Terveys", "color": "#FFEAA7", "icon": "💊"},
            {"name": "Vaatteet", "color": "#DDA0DD", "icon": "👕"},
            {"name": "Koulutus", "color": "#98D8C8", "icon": "📚"},
            {"name": "Sijoitukset", "color": "#F7DC6F", "icon": "📈"},
            {"name": "Säästöt", "color": "#BB8FCE", "icon": "💰"},
            {"name": "Palkka", "color": "#85C1E9", "icon": "💼"},
            {"name": "Freelance", "color": "#F8C471", "icon": "💻"},
            {"name": "Sivutulot", "color": "#82E0AA", "icon": "🎯"},
            {"name": "Lainat", "color": "#F1948A", "icon": "🏦"},
            {"name": "Laskut", "color": "#F7DC6F", "icon": "📄"},
            {"name": "Muu", "color": "#BDC3C7", "icon": "📌"}
        ]
        
        for cat_data in default_categories:
            category = Category(
                name=cat_data["name"],
                color=cat_data["color"],
                icon=cat_data["icon"],
                is_default=True
            )
            db.add(category)
        
        db.commit()
        logger.info(f"Initialized {len(default_categories)} default categories")
        
    except Exception as e:
        logger.error(f"Failed to initialize categories: {e}")
        db.rollback()
    finally:
        db.close()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test database connection
def test_db_connection():
    """Test database connection."""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Can be run directly to initialize database
    init_db() 