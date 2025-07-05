"""
API module for Personal Finance Agent.

This module contains all the API route handlers organized by functionality:
- auth: Authentication and user management
- documents: Document upload and OCR processing
- transactions: Transaction CRUD and categorization
- categories: Category management and statistics
- dashboard: Financial analytics and insights

All routers are available for import and inclusion in the main FastAPI application.
"""

# Import all API routers for easy access
from . import auth, transactions, categories, dashboard #, documents

__all__ = [
    "auth",
    "documents", 
    "transactions",
    "categories",
    "dashboard"
]
