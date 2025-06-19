"""
Recommendation model for AI-generated financial advice and suggestions.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.db.base import Base


class RecommendationType(PyEnum):
    """Type of recommendation."""
    SAVINGS_OPPORTUNITY = "savings_opportunity"
    BUDGET_ADJUSTMENT = "budget_adjustment"
    SPENDING_ALERT = "spending_alert"
    GOAL_PROGRESS = "goal_progress"
    CATEGORY_OPTIMIZATION = "category_optimization"
    DUPLICATE_SUBSCRIPTION = "duplicate_subscription"
    ACHIEVEMENT = "achievement"
    GENERAL_ADVICE = "general_advice"


class RecommendationStatus(PyEnum):
    """Status of recommendation."""
    PROPOSED = "proposed"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    IMPLEMENTED = "implemented"
    EXPIRED = "expired"


class RecommendationPriority(PyEnum):
    """Priority level of recommendation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Recommendation(Base):
    """
    Recommendation model for storing AI-generated financial advice and suggestions.
    Tracks user engagement and implementation of recommendations.
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Recommendation content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    detailed_explanation = Column(Text, nullable=True)
    
    # Classification and metadata
    recommendation_type = Column(Enum(RecommendationType), nullable=False, index=True)
    priority = Column(Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PROPOSED, index=True)
    
    # Financial impact
    potential_savings = Column(Float, nullable=True)  # Estimated savings in EUR
    impact_timeframe_days = Column(Integer, nullable=True)  # Expected timeframe for impact
    confidence_score = Column(Float, nullable=True)  # AI confidence in recommendation
    
    # Action items and implementation
    action_required = Column(Boolean, default=False)
    action_description = Column(Text, nullable=True)
    action_url = Column(String, nullable=True)  # Link to relevant UI section
    
    # Personalization and context
    reasoning = Column(Text, nullable=True)  # Why this recommendation was generated
    data_source = Column(String, nullable=True)  # What data triggered this recommendation
    related_category_ids = Column(String, nullable=True)  # Comma-separated category IDs
    related_transaction_ids = Column(String, nullable=True)  # Comma-separated transaction IDs
    
    # User interaction
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    user_feedback = Column(Text, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 rating from user
    
    # Lifecycle and expiry
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_recurring = Column(Boolean, default=False)  # Can this recommendation recur?
    recurrence_interval_days = Column(Integer, nullable=True)
    last_occurrence = Column(DateTime(timezone=True), nullable=True)
    
    # AI/ML metadata
    generated_by_model = Column(String, nullable=True)  # Which AI model generated this
    model_version = Column(String, nullable=True)
    generation_context = Column(Text, nullable=True)  # Context used for generation
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships  
    user = relationship("User", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, type={self.recommendation_type}, title='{self.title}', status={self.status})>"
    
    @property
    def is_active(self):
        """Check if recommendation is still active."""
        return self.status in [RecommendationStatus.PROPOSED, RecommendationStatus.VIEWED]
    
    @property
    def is_expired(self):
        """Check if recommendation has expired."""
        if not self.expires_at:
            return False
        return self.expires_at < func.now()
    
    @property
    def days_since_created(self):
        """Days since recommendation was created."""
        from datetime import datetime
        return (datetime.now() - self.created_at).days
    
    @property
    def engagement_score(self):
        """Calculate engagement score based on user interaction."""
        score = 0
        if self.viewed_at:
            score += 1
        if self.responded_at:
            score += 2
        if self.user_rating:
            score += self.user_rating
        if self.status == RecommendationStatus.IMPLEMENTED:
            score += 5
        return score
    
    def mark_viewed(self):
        """Mark recommendation as viewed by user."""
        if self.status == RecommendationStatus.PROPOSED:
            self.status = RecommendationStatus.VIEWED
            self.viewed_at = func.now()
    
    def mark_accepted(self, feedback: str = None):
        """Mark recommendation as accepted by user."""
        self.status = RecommendationStatus.ACCEPTED
        self.responded_at = func.now()
        if feedback:
            self.user_feedback = feedback
    
    def mark_dismissed(self, feedback: str = None):
        """Mark recommendation as dismissed by user."""
        self.status = RecommendationStatus.DISMISSED
        self.responded_at = func.now()
        if feedback:
            self.user_feedback = feedback
    
    def mark_implemented(self):
        """Mark recommendation as implemented."""
        self.status = RecommendationStatus.IMPLEMENTED
    
    def add_user_rating(self, rating: int, feedback: str = None):
        """Add user rating and feedback."""
        if 1 <= rating <= 5:
            self.user_rating = rating
            if feedback:
                self.user_feedback = feedback 