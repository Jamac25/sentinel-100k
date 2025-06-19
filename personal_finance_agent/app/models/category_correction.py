"""
CategoryCorrection model for machine learning feedback loop.
This is crucial for the agent's learning system as specified in the architecture.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class CategoryCorrection(Base):
    """
    CategoryCorrection model for storing user corrections to transaction categorization.
    
    This model is critical for the learning system. When users correct a transaction's category,
    the correction is stored here to create high-quality, user-verified training data.
    Background processes can query this table to retrain and improve the categorization model.
    
    This transforms the database from a simple data store into an active part of the AI learning cycle,
    implementing the adaptive behavior described in the specification.
    """
    __tablename__ = "category_corrections"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Original categorization details
    original_text = Column(Text, nullable=False, index=True)  # Transaction description that was categorized
    original_category_id = Column(Integer, nullable=True)  # What the AI originally predicted (if any)
    original_confidence = Column(Float, nullable=True)  # AI's confidence in original prediction
    
    # User correction
    corrected_category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    correction_reason = Column(String, nullable=True)  # Why user made this correction
    
    # Context for better learning
    transaction_amount = Column(Float, nullable=True)
    transaction_date = Column(DateTime(timezone=True), nullable=True)
    merchant_name = Column(String, nullable=True)
    raw_ocr_text = Column(Text, nullable=True)  # Full OCR text if available
    
    # Learning metadata
    model_version_corrected = Column(String, nullable=True)  # Which model version made the error
    features_used = Column(Text, nullable=True)  # JSON of features that were used for prediction
    is_training_sample = Column(Boolean, default=True)  # Whether to include in training
    
    # Quality and validation
    correction_confidence = Column(Float, default=1.0)  # How confident we are in the correction
    validated_by_system = Column(Boolean, default=False)  # System validation of correction
    user_expertise_score = Column(Float, default=1.0)  # User's expertise level for weighting
    
    # Learning impact tracking
    used_for_training = Column(Boolean, default=False)
    training_batch_id = Column(String, nullable=True)  # Which training batch included this
    model_improvement_score = Column(Float, nullable=True)  # How much this correction improved the model
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    used_for_training_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="category_corrections")
    transaction = relationship("Transaction", back_populates="category_corrections")
    corrected_category = relationship("Category")
    
    def __repr__(self):
        return f"<CategoryCorrection(id={self.id}, transaction_id={self.transaction_id}, original='{self.original_text[:30]}...', corrected_category_id={self.corrected_category_id})>"
    
    @property
    def is_new_correction(self):
        """Check if this correction hasn't been used for training yet."""
        return not self.used_for_training
    
    @property
    def training_weight(self):
        """Calculate training weight based on correction quality and user expertise."""
        base_weight = self.correction_confidence * self.user_expertise_score
        
        # Boost recent corrections (they reflect current spending patterns)
        days_old = (func.now() - self.created_at).days if self.created_at else 0
        recency_factor = max(0.5, 1.0 - (days_old / 365))  # Decay over a year
        
        return base_weight * recency_factor
    
    @property
    def learning_features(self):
        """Extract learning features from this correction."""
        features = {
            "text": self.original_text.lower(),
            "amount": self.transaction_amount,
            "merchant": self.merchant_name.lower() if self.merchant_name else None,
            "corrected_category": self.corrected_category_id,
            "weight": self.training_weight
        }
        
        # Add temporal features
        if self.transaction_date:
            features.update({
                "day_of_week": self.transaction_date.weekday(),
                "month": self.transaction_date.month,
                "hour": self.transaction_date.hour if hasattr(self.transaction_date, 'hour') else None
            })
        
        return features
    
    def mark_used_for_training(self, batch_id: str, improvement_score: float = None):
        """Mark this correction as used for model training."""
        self.used_for_training = True
        self.training_batch_id = batch_id
        self.used_for_training_at = func.now()
        if improvement_score:
            self.model_improvement_score = improvement_score
    
    def validate_correction(self, is_valid: bool, reason: str = None):
        """Validate or invalidate this correction."""
        self.validated_by_system = is_valid
        if not is_valid:
            self.is_training_sample = False
            self.correction_reason = f"Invalid: {reason}" if reason else "Invalid correction"
    
    @classmethod
    def get_training_data(cls, session, limit: int = None, min_confidence: float = 0.5):
        """
        Get high-quality training data for model retraining.
        This is the key method that background processes will use.
        """
        query = session.query(cls).filter(
            cls.is_training_sample == True,
            cls.correction_confidence >= min_confidence,
            cls.used_for_training == False
        ).order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod  
    def get_learning_statistics(cls, session):
        """Get statistics about the learning data quality."""
        total_corrections = session.query(cls).count()
        unused_corrections = session.query(cls).filter(cls.used_for_training == False).count()
        high_confidence = session.query(cls).filter(cls.correction_confidence >= 0.8).count()
        
        return {
            "total_corrections": total_corrections,
            "unused_corrections": unused_corrections,
            "high_confidence_corrections": high_confidence,
            "learning_readiness": unused_corrections >= 10  # Need at least 10 corrections to retrain
        } 