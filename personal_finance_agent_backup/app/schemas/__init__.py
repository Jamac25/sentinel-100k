"""
Pydantic schemas for Personal Finance Agent API.

This module provides all the request/response schemas used by the FastAPI endpoints.
All schemas are imported and available for use in API route handlers.
"""

# Import all schemas from individual modules
from .user import UserCreate, UserUpdate, UserResponse, UserInDB
from .category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryInDB
from .transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse, 
    TransactionInDB, TransactionWithCategory
)
from .dashboard import (
    DashboardSummary, DashboardFilters, BudgetStatus, AgentStatus,
    RecentTransaction, SpendingByCategory, GoalProgress, MonthlyTrend,
    CategoryBreakdown, TransactionFilters, TransactionStats, 
    CategorySuggestion, CategoryStats
)
from .auth import (
    UserLogin, Token, PasswordChange, PasswordReset
)
from .document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentStats,
    DocumentType, ProcessingStatus
)

# Export all schemas for easy import
__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserInDB",
    
    # Authentication schemas
    "UserLogin",
    "Token",
    "PasswordChange",
    "PasswordReset",
    
    # Category schemas
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse", 
    "CategoryInDB",
    "CategoryStats",
    "CategorySuggestion",
    
    # Transaction schemas
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionInDB",
    "TransactionWithCategory",
    "TransactionFilters",
    "TransactionStats",
    
    # Document schemas
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentStats",
    "DocumentType",
    "ProcessingStatus",
    
    # Dashboard schemas
    "DashboardSummary",
    "DashboardFilters",
    "BudgetStatus",
    "AgentStatus",
    "RecentTransaction",
    "SpendingByCategory",
    "GoalProgress",
    "MonthlyTrend",
    "CategoryBreakdown",
]
