"""
Services module for the personal finance agent.
Contains business logic services for document processing, OCR, ML categorization, and scheduling.
"""

from .document_service import DocumentService
from .ocr_service import OCREngine, BaseOCRService, TesseractOCRService, GoogleVisionOCRService
from .categorization_service import TransactionCategorizationService
from .scheduler_service import SchedulerService, scheduler_service
from .event_bus import event_bus, EventBus, EventType, Event

__all__ = [
    # Document services
    "DocumentService",
    
    # OCR services
    "OCREngine",
    "BaseOCRService", 
    "TesseractOCRService",
    "GoogleVisionOCRService",
    
    # ML services
    "TransactionCategorizationService",
    
    # Automation services
    "SchedulerService",
    "scheduler_service",
    
    # Event bus
    "event_bus",
    "EventBus",
    "EventType",
    "Event",
]
