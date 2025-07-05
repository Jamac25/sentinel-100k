"""
Models package - SQLAlchemy ORM models for the Personal Finance Agent.

This module imports and exposes all database models, making them available
for imports throughout the application.
"""

# Import all models to make them available
from .user import User
from .transaction import Transaction
from .category import Category
from .document import Document, DocumentType, ProcessingStatus
from .budget import Budget
from .goal import Goal, GoalType, GoalStatus
from .recommendation import Recommendation
from .agent_state import AgentState
from .category_correction import CategoryCorrection

# Make all models available for easy import
__all__ = [
    "User",
    "Transaction", 
    "Category",
    "Document",
    "DocumentType",
    "ProcessingStatus",
    "Budget",
    "Goal",
    "GoalType",
    "GoalStatus",
    "Recommendation",
    "AgentState",
    "CategoryCorrection"
]
