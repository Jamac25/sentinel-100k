"""
Document service for handling file uploads and metadata storage.
"""
import os
import uuid
import hashlib
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models import Document, DocumentType, ProcessingStatus
from app.core.config import get_upload_path, settings
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service for handling document uploads, storage, and metadata management.
    Separates file storage from document processing for clean architecture.
    """
    
    def __init__(self):
        self.upload_path = get_upload_path()
        self.allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        self.max_file_size = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes
    
    async def upload_document(
        self, 
        file: UploadFile, 
        user_id: int, 
        db: Session,
        document_type: Optional[DocumentType] = None
    ) -> Document:
        """
        Upload and store a document file, creating metadata in database.
        
        Args:
            file: Uploaded file from FastAPI
            user_id: ID of the user uploading the file
            db: Database session
            document_type: Optional document type classification
            
        Returns:
            Document: Created document record with metadata
            
        Raises:
            HTTPException: If file validation fails
        """
        logger.info(f"Processing document upload for user {user_id}: {file.filename}")
        
        # Validate file
        self._validate_file(file)
        
        # Generate unique filename
        file_extension = self._get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_path, unique_filename)
        
        try:
            # Save file to disk
            file_content = await file.read()
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Calculate file hash for deduplication
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Detect document type if not provided
            if document_type is None:
                document_type = self._detect_document_type(file.filename, file.content_type)
            
            # Create document record
            document = Document(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(file_content),
                mime_type=file.content_type or "application/octet-stream",
                document_type=document_type,
                processing_status=ProcessingStatus.PENDING,
                user_id=user_id
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Document uploaded successfully: {document.id} ({document.file_size_mb} MB)")
            return document
            
        except Exception as e:
            # Cleanup file if database operation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Failed to upload document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file constraints."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension
        file_extension = self._get_file_extension(file.filename)
        if file_extension.lower() not in self.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Supported: {', '.join(self.allowed_extensions)}"
            )
        
        # Check file size (approximate, will be exact after reading)
        if hasattr(file, 'size') and file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {settings.max_upload_size_mb} MB"
            )
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        return os.path.splitext(filename)[1].lower()
    
    def _detect_document_type(self, filename: str, mime_type: Optional[str]) -> DocumentType:
        """Detect document type based on filename and MIME type."""
        filename_lower = filename.lower()
        
        if 'receipt' in filename_lower or 'kuitti' in filename_lower:
            return DocumentType.RECEIPT
        elif 'statement' in filename_lower or 'tiliote' in filename_lower:
            return DocumentType.BANK_STATEMENT
        elif 'invoice' in filename_lower or 'lasku' in filename_lower:
            return DocumentType.INVOICE
        elif 'tax' in filename_lower or 'vero' in filename_lower:
            return DocumentType.TAX_DOCUMENT
        else:
            return DocumentType.OTHER
    
    def get_document(self, document_id: int, user_id: int, db: Session) -> Optional[Document]:
        """Get document by ID, ensuring user ownership."""
        return db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
    
    def list_user_documents(
        self, 
        user_id: int, 
        db: Session, 
        skip: int = 0, 
        limit: int = 50,
        document_type: Optional[DocumentType] = None,
        processing_status: Optional[ProcessingStatus] = None
    ) -> List[Document]:
        """List documents for a user with optional filters."""
        query = db.query(Document).filter(Document.user_id == user_id)
        
        if document_type:
            query = query.filter(Document.document_type == document_type)
        
        if processing_status:
            query = query.filter(Document.processing_status == processing_status)
        
        return query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    def delete_document(self, document_id: int, user_id: int, db: Session) -> bool:
        """Delete document and its file."""
        document = self.get_document(document_id, user_id, db)
        if not document:
            return False
        
        try:
            # Delete file from disk
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete database record
            db.delete(document)
            db.commit()
            
            logger.info(f"Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            db.rollback()
            return False
    
    def get_processing_queue(self, db: Session, limit: int = 10) -> List[Document]:
        """Get documents pending processing for background workers."""
        return db.query(Document).filter(
            Document.processing_status == ProcessingStatus.PENDING
        ).order_by(Document.created_at.asc()).limit(limit).all()
    
    def mark_processing_started(self, document_id: int, db: Session) -> bool:
        """Mark document as processing started."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.mark_processing_started()
            db.commit()
            return True
        return False
    
    def mark_processing_completed(
        self, 
        document_id: int, 
        db: Session,
        extracted_text: Optional[str] = None,
        extraction_confidence: Optional[float] = None,
        ocr_service_used: Optional[str] = None
    ) -> bool:
        """Mark document processing as completed with results."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.mark_processing_completed()
            if extracted_text:
                document.extracted_text = extracted_text
            if extraction_confidence:
                document.extraction_confidence = extraction_confidence
            if ocr_service_used:
                document.ocr_service_used = ocr_service_used
            db.commit()
            return True
        return False
    
    def mark_processing_failed(self, document_id: int, db: Session, error_message: str) -> bool:
        """Mark document processing as failed."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.mark_processing_failed(error_message)
            db.commit()
            return True
        return False
    
    def get_storage_stats(self, user_id: int, db: Session) -> dict:
        """Get storage statistics for a user."""
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        
        total_size = sum(doc.file_size for doc in documents)
        total_count = len(documents)
        processed_count = sum(1 for doc in documents if doc.is_processed)
        failed_count = sum(1 for doc in documents if doc.has_failed)
        
        return {
            "total_documents": total_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "processed_documents": processed_count,
            "failed_documents": failed_count,
            "processing_success_rate": (processed_count / total_count * 100) if total_count > 0 else 0
        } 