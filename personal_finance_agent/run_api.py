#!/usr/bin/env python3
"""
Startup script for Personal Finance Agent API

This script starts the FastAPI application with proper configuration
for development or production use.
"""
import os
import sys
import uvicorn
import logging
from pathlib import Path
from app.main import app

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Start the FastAPI application."""
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    logger.info(f"Database URL: {settings.database_url[:20]}...")
    
    # Check if .env file exists
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        logger.warning(".env file not found. Using default configuration.")
        logger.warning("For production use, please create a .env file with proper configuration.")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main() 