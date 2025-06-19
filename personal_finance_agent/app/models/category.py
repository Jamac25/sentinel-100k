"""
Category model for expense and income classification.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Category(Base):
    """
    Category model for classifying transactions into expense/income categories.
    Examples: "Groceries", "Rent", "Salary", "Entertainment"
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Category type and properties
    is_income = Column(Boolean, default=False)  # True for income categories, False for expenses
    is_essential = Column(Boolean, default=False)  # True for essential expenses (rent, utilities)
    color = Column(String, default="#6B7280")  # Hex color for UI visualization
    icon = Column(String, nullable=True)  # Icon name for UI
    
    # Category hierarchy (for subcategories)
    parent_id = Column(Integer, nullable=True)  # Self-referencing for subcategories
    
    # ML and classification metadata
    keywords = Column(Text, nullable=True)  # Comma-separated keywords for auto-classification
    confidence_threshold = Column(Float, default=0.7)  # Minimum confidence for auto-assignment
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Usage statistics
    usage_count = Column(Integer, default=0)  # Number of transactions in this category
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', is_income={self.is_income})>"
    
    @property
    def type_label(self):
        """Human-readable category type label."""
        return "Income" if self.is_income else "Expense"
    
    def increment_usage(self):
        """Increment usage statistics when category is used."""
        self.usage_count += 1
        self.last_used = func.now() 