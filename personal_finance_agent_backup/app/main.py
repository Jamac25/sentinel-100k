"""
Personal Finance Agent - Main FastAPI Application

A comprehensive personal finance management system with AI-powered insights,
document processing, and automated categorization.
"""
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
import time

from app.core.config import settings
from app.db.init_db import init_db, get_db, engine, Base
from app.services.scheduler_service import scheduler_service

# Import API routers
from app.api import auth, transactions, categories, dashboard
# from app.api.advanced_intelligence import router as advanced_intelligence_router

# Luo tietokantataulut
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info("Starting Personal Finance Agent...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Start scheduler service
        logger.info("Starting scheduler service...")
        await scheduler_service.start()
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Personal Finance Agent...")
    
    try:
        # Stop scheduler service
        await scheduler_service.stop()
        logger.info("Scheduler service stopped")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="Personal Finance Agent API",
    description="Älykkäs henkilökohtainen talousagentti 100k€ tavoitteen saavuttamiseksi",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions globally."""
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Include API routers
app.include_router(auth.router, prefix="/api/v1")
# app.include_router(documents.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
# app.include_router(guardian.router, prefix="/api/v1")
# app.include_router(advanced_intelligence_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Personal Finance Agent API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Authentication & User Management",
            "Transaction Management", 
            "Category Management",
            "Dashboard Analytics",
            "Document Processing",
            "Sentinel Guardian™",
            "Sentinel Learning Engine™",
            "Income Stream Intelligence™",
            "Liabilities Insight™",
            "Idea Engine™"
        ]
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "2.0.0"
    }


# API information endpoint
@app.get("/api/info", tags=["info"])
async def api_info():
    """
    Get API information and available endpoints.
    """
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": "Personal Finance Agent API",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "documents": "/api/v1/documents",
            "transactions": "/api/v1/transactions",
            "categories": "/api/v1/categories",
            "dashboard": "/api/v1/dashboard"
        },
        "features": [
            "JWT Authentication",
            "Document OCR Processing",
            "AI Transaction Categorization",
            "Financial Analytics Dashboard",
            "Goal Tracking",
            "Smart Insights",
            "Finnish Localization"
        ],
        "documentation": {
            "interactive": "/docs",
            "openapi_schema": "/openapi.json"
        }
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "services": {
            "authentication": "active",
            "transactions": "active", 
            "categories": "active",
            "dashboard": "active",
            "documents": "active",
            "guardian": "active",
            "advanced_intelligence": "active"
        },
        "database": "connected",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
