"""
User model for authentication and profile management.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    """
    User model for storing user account information.
    Includes secure password hashing and profile data.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # User preferences and settings
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    preferred_currency = Column(String, default="EUR")
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    
    # Financial profile
    monthly_income = Column(Float, nullable=True)
    savings_goal = Column(Float, default=100000.0)  # Default €100,000 goal
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    agent_state = relationship("AgentState", back_populates="user", uselist=False, cascade="all, delete-orphan")
    category_corrections = relationship("CategoryCorrection", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>" 