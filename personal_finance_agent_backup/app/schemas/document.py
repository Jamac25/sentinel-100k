"""
Pydantic schemas for document endpoints.
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""
    RECEIPT = "receipt"
    INVOICE = "invoice"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Document processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentCreate(BaseModel):
    """Schema for document creation requests."""
    document_type: Optional[DocumentType] = None
    description: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Schema for document update requests."""
    document_type: Optional[DocumentType] = None
    description: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document responses."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_size_mb: float
    mime_type: str
    document_type: Optional[DocumentType]
    processing_status: ProcessingStatus
    extracted_text: Optional[str]
    extraction_confidence: Optional[float]
    ocr_service_used: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentStats(BaseModel):
    """Schema for document storage statistics."""
    total_documents: int
    total_size_mb: float
    processed_documents: int
    failed_documents: int
    processing_success_rate: float 