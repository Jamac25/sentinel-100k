"""
Transaction model for all financial transactions.
The central model that tracks all income and expenses.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.db.base import Base


class TransactionStatus(PyEnum):
    """Transaction processing status."""
    PENDING = "pending"
    PROCESSED = "processed"
    VERIFIED = "verified"
    REJECTED = "rejected"


class TransactionSource(PyEnum):
    """Source of transaction data."""
    MANUAL = "manual"
    OCR_RECEIPT = "ocr_receipt"
    OCR_STATEMENT = "ocr_statement"
    BANK_API = "bank_api"
    CSV_IMPORT = "csv_import"


class Transaction(Base):
    """
    Transaction model for storing all financial transactions.
    Central model that connects users, categories, and documents.
    """
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core transaction data
    amount = Column(Float, nullable=False, index=True)
    description = Column(Text, nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Transaction classification
    is_income = Column(Boolean, default=False, index=True)
    
    # Processing metadata
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    source = Column(Enum(TransactionSource), default=TransactionSource.MANUAL)
    confidence_score = Column(Float, nullable=True)  # ML classification confidence
    
    # Additional transaction details
    merchant = Column(String, nullable=True, index=True)
    location = Column(String, nullable=True)
    reference_number = Column(String, nullable=True)
    account = Column(String, nullable=True)  # Bank account or payment method
    
    # OCR and processing metadata
    raw_text = Column(Text, nullable=True)  # Original OCR text for learning
    processing_notes = Column(Text, nullable=True)  # Any processing issues or notes
    
    # User feedback and corrections
    user_verified = Column(Boolean, default=False)
    needs_attention = Column(Boolean, default=False)  # Flag for transactions needing user review
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)  # Source document if any
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    document = relationship("Document", back_populates="transactions")
    category_corrections = relationship("CategoryCorrection", back_populates="transaction")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description='{self.description[:30]}...', date={self.transaction_date})>"
    
    @property
    def amount_display(self):
        """Formatted amount for display."""
        sign = "+" if self.is_income else "-"
        return f"{sign}€{abs(self.amount):.2f}"
    
    @property
    def is_processed(self):
        """Check if transaction has been fully processed."""
        return self.status in [TransactionStatus.PROCESSED, TransactionStatus.VERIFIED]
    
    @property
    def needs_categorization(self):
        """Check if transaction needs category assignment."""
        return self.category_id is None and self.status != TransactionStatus.REJECTED
    
    def mark_processed(self):
        """Mark transaction as processed."""
        self.status = TransactionStatus.PROCESSED
        self.processed_at = func.now()
    
    def mark_verified(self):
        """Mark transaction as user-verified."""
        self.status = TransactionStatus.VERIFIED
        self.user_verified = True
        self.needs_attention = False 