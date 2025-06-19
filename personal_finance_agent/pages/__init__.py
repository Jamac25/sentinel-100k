"""
Pages module for Personal Finance Agent Streamlit app.
Contains all page components for the web interface.
"""

from .transactions import show_transactions_page
from .documents import show_documents_page
from .analytics import show_analytics_page
from .goals import show_goals_page
from .settings import show_settings_page
from .guardian import show_guardian_page
from .intelligence import show_intelligence_page

__all__ = [
    "show_transactions_page",
    "show_documents_page", 
    "show_analytics_page",
    "show_goals_page",
    "show_settings_page",
    "show_guardian_page",
    "show_intelligence_page"
] 