"""
Goal model for savings goals and financial milestones.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime, date
from app.db.base import Base


class GoalType(PyEnum):
    """Type of financial goal."""
    SAVINGS = "savings"
    DEBT_PAYOFF = "debt_payoff"
    INVESTMENT = "investment"
    EMERGENCY_FUND = "emergency_fund"
    CUSTOM = "custom"


class GoalStatus(PyEnum):
    """Goal achievement status."""
    ACTIVE = "active"
    ACHIEVED = "achieved"
    PAUSED = "paused"
    ABANDONED = "abandoned"
    OVERDUE = "overdue"


class GoalPriority(PyEnum):
    """Goal priority level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Goal(Base):
    """
    Goal model for storing savings goals and financial milestones.
    Supports the primary €100,000 goal and intermediate milestones.
    """
    __tablename__ = "goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Goal definition
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(Enum(GoalType), default=GoalType.SAVINGS)
    priority = Column(Enum(GoalPriority), default=GoalPriority.MEDIUM)
    
    # Financial targets
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    monthly_target = Column(Float, nullable=True)  # Monthly savings target
    
    # Timeline
    target_date = Column(DateTime(timezone=True), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    achieved_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status and progress
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE, index=True)
    progress_percentage = Column(Float, default=0.0)
    
    # Motivation and gamification
    icon = Column(String, nullable=True)  # Emoji or icon name
    color = Column(String, default="#10B981")  # Theme color
    celebration_message = Column(Text, nullable=True)  # Message when achieved
    
    # Milestones and sub-goals
    is_milestone = Column(Boolean, default=False)  # True for intermediate milestones
    parent_goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)  # For milestone hierarchy
    milestone_percentage = Column(Float, nullable=True)  # Percentage of parent goal
    
    # Automation and tracking
    auto_track = Column(Boolean, default=True)  # Automatically track progress
    track_category_ids = Column(String, nullable=True)  # Comma-separated category IDs to track
    
    # Notifications
    send_progress_updates = Column(Boolean, default=True)
    update_frequency_days = Column(Integer, default=7)  # How often to send updates
    last_update_sent = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_progress_update = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    milestones = relationship("Goal", backref="parent_goal", remote_side=[id])
    
    def __repr__(self):
        return f"<Goal(id={self.id}, title='{self.title}', target={self.target_amount}, current={self.current_amount}, status={self.status})>"
    
    @property
    def remaining_amount(self):
        """Amount remaining to reach goal."""
        return max(self.target_amount - self.current_amount, 0)
    
    @property
    def is_achieved(self):
        """Check if goal is achieved."""
        return self.current_amount >= self.target_amount
    
    @property
    def days_remaining(self):
        """Days remaining to reach target date."""
        if not self.target_date:
            return None
        today = datetime.now().date()
        target_date = self.target_date.date() if isinstance(self.target_date, datetime) else self.target_date
        return max((target_date - today).days, 0)
    
    @property
    def daily_savings_needed(self):
        """Daily savings needed to reach goal by target date."""
        if not self.target_date or self.days_remaining <= 0:
            return 0
        return self.remaining_amount / self.days_remaining
    
    @property
    def monthly_progress_needed(self):
        """Monthly savings needed if monthly target is set."""
        if not self.monthly_target:
            return None
        months_remaining = (self.days_remaining or 0) / 30.44  # Average days per month
        if months_remaining <= 0:
            return self.remaining_amount
        return self.remaining_amount / months_remaining
    
    @property
    def is_on_track(self):
        """Check if goal progress is on track."""
        if not self.target_date:
            return True
        
        total_days = (self.target_date.date() - self.start_date.date()).days
        days_elapsed = (datetime.now().date() - self.start_date.date()).days
        
        if total_days <= 0:
            return True
            
        expected_progress = (days_elapsed / total_days) * self.target_amount
        return self.current_amount >= expected_progress * 0.9  # 10% tolerance
    
    def update_progress(self, new_amount: float):
        """Update goal progress."""
        self.current_amount = new_amount
        self.progress_percentage = min((self.current_amount / self.target_amount) * 100, 100)
        self.last_progress_update = func.now()
        
        # Check if goal is achieved
        if self.is_achieved and self.status == GoalStatus.ACTIVE:
            self.status = GoalStatus.ACHIEVED
            self.achieved_date = func.now()
        
        # Check if goal is overdue
        if self.target_date and self.target_date < datetime.now() and not self.is_achieved:
            self.status = GoalStatus.OVERDUE
    
    def create_milestone(self, title: str, percentage: float):
        """Create a milestone for this goal."""
        if self.is_milestone:
            raise ValueError("Cannot create milestone for a milestone")
        
        milestone_amount = self.target_amount * (percentage / 100)
        milestone = Goal(
            title=title,
            target_amount=milestone_amount,
            goal_type=self.goal_type,
            parent_goal_id=self.id,
            is_milestone=True,
            milestone_percentage=percentage,
            user_id=self.user_id,
            start_date=self.start_date,
            target_date=self.target_date
        )
        return milestone 