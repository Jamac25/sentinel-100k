"""
OCR Service for document text extraction.
Supports multiple OCR engines with fallback mechanisms.
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import cv2
import numpy as np

# Try to import OCR libraries, but don't fail if they're missing
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF not available")

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logging.warning("Google Vision not available")

logger = logging.getLogger(__name__)

class BaseOCRService(ABC):
    """Base class for OCR services."""
    
    @abstractmethod
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """Extract text from image and return (text, confidence)."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this OCR service is available."""
        pass

class MockOCRService(BaseOCRService):
    """Mock OCR service for testing when real OCR is not available."""
    
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """Return mock text for testing."""
        logger.info(f"Mock OCR: Processing {image_path}")
        return "MOCK OCR TEXT - Testing mode", 0.8
    
    def is_available(self) -> bool:
        """Always available for testing."""
        return True

class TesseractOCRService(BaseOCRService):
    """Tesseract OCR service implementation."""
    
    def __init__(self):
        """Initialize Tesseract OCR service."""
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract not available")
        
        try:
            # Check if tesseract is installed
            pytesseract.get_tesseract_version()
            self.available = True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            self.available = False
    
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """Extract text using Tesseract OCR."""
        if not self.available:
            raise RuntimeError("Tesseract OCR not available")
        
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Preprocess image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract text
            text = pytesseract.image_to_string(gray, lang='eng+fin')
            
            # Get confidence (simplified)
            confidence = 0.8  # Mock confidence for now
            
            logger.info(f"Tesseract OCR: Extracted {len(text)} characters from {image_path}")
            return text.strip(), confidence
            
        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Tesseract is available."""
        return self.available

class GoogleVisionOCRService(BaseOCRService):
    """Google Vision OCR service implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google Vision OCR service."""
        if not GOOGLE_VISION_AVAILABLE:
            raise RuntimeError("Google Vision not available")
        
        self.api_key = api_key
        self.client = vision.ImageAnnotatorClient()
        self.available = True
    
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """Extract text using Google Vision OCR."""
        if not self.available:
            raise RuntimeError("Google Vision OCR not available")
        
        try:
            # Read image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create image object
            image = vision.Image(content=content)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                # Get full text
                text = texts[0].description
                
                # Calculate average confidence
                confidence = sum(t.confidence for t in texts[1:]) / len(texts[1:]) if len(texts) > 1 else 0.8
                
                logger.info(f"Google Vision OCR: Extracted {len(text)} characters from {image_path}")
                return text.strip(), confidence
            else:
                return "", 0.0
                
        except Exception as e:
            logger.error(f"Google Vision OCR error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Google Vision is available."""
        return self.available

class OCREngine:
    """Main OCR engine that manages multiple OCR services."""
    
    def __init__(self, preferred_service: str = "tesseract"):
        """Initialize OCR engine with preferred service."""
        self.preferred_service = preferred_service
        self.ocr_service = self._create_ocr_service()
        logger.info(f"OCR Engine initialized with {self.preferred_service}")
    
    def _create_ocr_service(self) -> BaseOCRService:
        """Create OCR service based on preference and availability."""
        
        # Try preferred service first
        if self.preferred_service == "tesseract":
            try:
                if TESSERACT_AVAILABLE:
                    return TesseractOCRService()
                else:
                    logger.warning("Tesseract not available, trying Google Vision")
            except Exception as e:
                logger.warning(f"Tesseract failed: {e}")
        
        # Try Google Vision
        if self.preferred_service == "google_vision" or self.preferred_service == "tesseract":
            try:
                if GOOGLE_VISION_AVAILABLE:
                    return GoogleVisionOCRService()
                else:
                    logger.warning("Google Vision not available")
            except Exception as e:
                logger.warning(f"Google Vision failed: {e}")
        
        # Fallback to mock service for testing
        logger.warning("No OCR service available, using mock service for testing")
        return MockOCRService()
    
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """Extract text from image using available OCR service."""
        return self.ocr_service.extract_text(image_path)
    
    def is_available(self) -> bool:
        """Check if any OCR service is available."""
        return self.ocr_service.is_available()
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available OCR services."""
        return {
            "preferred_service": self.preferred_service,
            "tesseract_available": TESSERACT_AVAILABLE,
            "google_vision_available": GOOGLE_VISION_AVAILABLE,
            "current_service": type(self.ocr_service).__name__,
            "service_available": self.is_available()
        }

# Global OCR engine instance
ocr_engine = OCREngine() 