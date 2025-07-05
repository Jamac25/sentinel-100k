"""
User model for authentication and profile management.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    """
    User model for storing user account information.
    Includes secure password hashing and profile data.
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # User preferences and settings
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    preferred_currency = Column(String, default="EUR")
    language = Column(String, default="fi")  # Changed default to Finnish
    timezone = Column(String, default="Europe/Helsinki")  # Changed to Finnish timezone
    
    # Financial profile
    monthly_income = Column(Float, nullable=True)
    savings_goal = Column(Float, default=100000.0)  # Default €100,000 goal
    current_savings = Column(Float, default=0.0)  # Current savings amount
    
    # Detailed income breakdown
    primary_job_income = Column(Float, nullable=True)  # Main job income (e.g., Terveystalo)
    business_income = Column(Float, nullable=True)     # Own business income
    other_income = Column(Float, nullable=True)        # Other income sources
    
    # Expense breakdown
    housing_costs = Column(Float, nullable=True)       # Rent, utilities, etc.
    food_costs = Column(Float, nullable=True)          # Monthly food budget
    transport_costs = Column(Float, nullable=True)     # Transport costs
    entertainment_costs = Column(Float, nullable=True) # Entertainment & clothing
    family_support = Column(Float, nullable=True)      # Family support payments
    other_expenses = Column(Float, nullable=True)      # Other regular expenses
    
    # Personal information
    profession = Column(String, nullable=True)         # Current profession
    workplace = Column(String, nullable=True)          # Workplace name
    family_info = Column(Text, nullable=True)          # Information about family
    financial_goals = Column(Text, nullable=True)      # Personal financial goals
    
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
    
    @property
    def total_monthly_expenses(self):
        """Calculate total monthly expenses"""
        expenses = [
            self.housing_costs or 0,
            self.food_costs or 0,
            self.transport_costs or 0,
            self.entertainment_costs or 0,
            self.family_support or 0,
            self.other_expenses or 0
        ]
        return sum(expenses)
    
    @property
    def monthly_savings_potential(self):
        """Calculate potential monthly savings"""
        return (self.monthly_income or 0) - self.total_monthly_expenses
    
    @property
    def savings_rate_percentage(self):
        """Calculate savings rate as percentage"""
        if not self.monthly_income or self.monthly_income == 0:
            return 0.0
        return (self.monthly_savings_potential / self.monthly_income) * 100
    
    @property
    def months_to_goal(self):
        """Calculate months to reach savings goal"""
        if not self.monthly_savings_potential or self.monthly_savings_potential <= 0:
            return None
        remaining_amount = (self.savings_goal or 100000) - (self.current_savings or 0)
        return remaining_amount / self.monthly_savings_potential 