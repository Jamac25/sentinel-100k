"""
Budget model for storing user budgets by category and time period.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime, date
from app.db.base import Base


class BudgetPeriod(PyEnum):
    """Budget time period."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetStatus(PyEnum):
    """Budget status."""
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    PAUSED = "paused"
    COMPLETED = "completed"


class Budget(Base):
    """
    Budget model for storing user budgets for specific categories and time periods.
    Supports rolling budgets and automatic recalculation.
    """
    __tablename__ = "budgets"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Budget definition
    name = Column(String, nullable=False)  # User-friendly budget name
    amount = Column(Float, nullable=False)  # Budget amount
    period = Column(Enum(BudgetPeriod), default=BudgetPeriod.MONTHLY)
    
    # Time period
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Budget tracking
    spent_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, nullable=False)  # Calculated field
    status = Column(Enum(BudgetStatus), default=BudgetStatus.ACTIVE, index=True)
    
    # Alerts and notifications
    alert_threshold = Column(Float, default=0.8)  # Alert when 80% spent
    alert_sent = Column(Boolean, default=False)
    exceeded_alert_sent = Column(Boolean, default=False)
    
    # Auto-renewal
    is_recurring = Column(Boolean, default=True)
    auto_adjust = Column(Boolean, default=False)  # Auto-adjust based on spending patterns
    
    # Forecasting and AI
    predicted_spending = Column(Float, nullable=True)  # AI prediction for period
    confidence_score = Column(Float, nullable=True)  # Confidence in prediction
    last_prediction_update = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_calculated = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
    
    def __repr__(self):
        return f"<Budget(id={self.id}, name='{self.name}', amount={self.amount}, period={self.period}, status={self.status})>"
    
    @property
    def progress_percentage(self):
        """Budget usage percentage."""
        if self.amount <= 0:
            return 0
        return min((self.spent_amount / self.amount) * 100, 100)
    
    @property
    def is_exceeded(self):
        """Check if budget is exceeded."""
        return self.spent_amount > self.amount
    
    @property
    def is_near_limit(self):
        """Check if budget is near the alert threshold."""
        return (self.spent_amount / self.amount) >= self.alert_threshold if self.amount > 0 else False
    
    @property
    def days_remaining(self):
        """Days remaining in budget period."""
        today = datetime.now().date()
        end_date = self.end_date.date() if isinstance(self.end_date, datetime) else self.end_date
        return max((end_date - today).days, 0)
    
    @property
    def daily_remaining_budget(self):
        """Average daily budget remaining."""
        days_left = self.days_remaining
        if days_left <= 0:
            return 0
        return max(self.remaining_amount / days_left, 0) if self.remaining_amount > 0 else 0
    
    def update_spent_amount(self, new_spent: float):
        """Update spent amount and recalculate remaining."""
        self.spent_amount = new_spent
        self.remaining_amount = self.amount - self.spent_amount
        self.last_calculated = func.now()
        
        # Update status
        if self.is_exceeded:
            self.status = BudgetStatus.EXCEEDED
        elif self.remaining_amount <= 0:
            self.status = BudgetStatus.COMPLETED
        else:
            self.status = BudgetStatus.ACTIVE
    
    def check_alerts(self):
        """Check if alerts should be sent."""
        alerts_to_send = []
        
        if self.is_near_limit and not self.alert_sent:
            alerts_to_send.append("threshold")
            self.alert_sent = True
            
        if self.is_exceeded and not self.exceeded_alert_sent:
            alerts_to_send.append("exceeded")
            self.exceeded_alert_sent = True
            
        return alerts_to_send 