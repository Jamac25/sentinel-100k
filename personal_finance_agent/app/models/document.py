"""
Document model for uploaded file metadata.
Stores information about receipts, bank statements, and other financial documents.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.db.base import Base


class DocumentType(PyEnum):
    """Type of financial document."""
    RECEIPT = "receipt"
    BANK_STATEMENT = "bank_statement"
    INVOICE = "invoice"
    TAX_DOCUMENT = "tax_document"
    OTHER = "other"


class ProcessingStatus(PyEnum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


class Document(Base):
    """
    Document model for storing metadata about uploaded financial documents.
    Separates file metadata from actual object storage.
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File metadata
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)  # User's original filename
    file_path = Column(String, nullable=False)  # Storage path
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String, nullable=False)
    
    # Document classification
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    
    # Processing status and results
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, index=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_error = Column(Text, nullable=True)
    
    # OCR results
    extracted_text = Column(Text, nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    ocr_service_used = Column(String, nullable=True)  # Which OCR service was used
    
    # Parsed data from document
    extracted_amount = Column(Float, nullable=True)
    extracted_date = Column(DateTime(timezone=True), nullable=True)
    extracted_merchant = Column(String, nullable=True)
    parsing_confidence = Column(Float, nullable=True)
    
    # Manual review and verification
    requires_manual_review = Column(Boolean, default=False)
    reviewed_by_user = Column(Boolean, default=False)
    user_feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    transactions = relationship("Transaction", back_populates="document")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', type={self.document_type}, status={self.processing_status})>"
    
    @property
    def is_processed(self):
        """Check if document processing is completed."""
        return self.processing_status == ProcessingStatus.PROCESSED
    
    @property
    def has_failed(self):
        """Check if document processing failed."""
        return self.processing_status == ProcessingStatus.FAILED
    
    @property
    def file_size_mb(self):
        """File size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2) if self.file_size else 0
    
    def mark_processing_started(self):
        """Mark document processing as started."""
        self.processing_status = ProcessingStatus.PROCESSING
        self.processing_started_at = func.now()
    
    def mark_processing_completed(self):
        """Mark document processing as completed."""
        self.processing_status = ProcessingStatus.PROCESSED
        self.processing_completed_at = func.now()
    
    def mark_processing_failed(self, error_message: str):
        """Mark document processing as failed."""
        self.processing_status = ProcessingStatus.FAILED
        self.processing_error = error_message
        self.processing_completed_at = func.now() 