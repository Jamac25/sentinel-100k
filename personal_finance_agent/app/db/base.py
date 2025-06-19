"""
Database base configuration and engine setup.
Uses SQLAlchemy 2.0 with async support.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_database_url

# Database engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL query logging in development
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    Used by FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 