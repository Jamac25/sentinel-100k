"""
Pydantic schemas for dashboard and analytics endpoints.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class MonthlyTrend(BaseModel):
    """Schema for monthly financial trends."""
    month: str  # YYYY-MM format
    month_name: str  # Human readable month name
    income: float
    expenses: float
    net_amount: float
    transaction_count: int


class CategoryBreakdown(BaseModel):
    """Schema for category spending breakdown."""
    category_id: int
    category_name: str
    category_type: str
    category_color: Optional[str]
    total_amount: float
    transaction_count: int
    average_amount: float
    percentage: float
    last_transaction: Optional[datetime]


class GoalProgress(BaseModel):
    """Schema for goal progress tracking."""
    goal_id: int
    goal_name: str
    target_amount: float
    current_amount: float
    progress_percent: float
    target_date: Optional[date]
    days_remaining: Optional[int]
    status: str  # completed, on_track, behind, overdue


class DashboardSummary(BaseModel):
    """Schema for comprehensive dashboard summary."""
    period_days: int
    total_income: float
    total_expenses: float
    net_amount: float
    transaction_count: int
    avg_daily_spending: float
    expense_change_percent: float
    category_breakdown: Dict[str, Any]
    monthly_trends: List[MonthlyTrend]
    goal_progress: List[GoalProgress]
    agent_mood: int
    agent_message: str
    top_categories: List[Dict[str, Any]]


class TransactionFilters(BaseModel):
    """Schema for transaction filtering parameters."""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    category_id: Optional[int] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search: Optional[str] = None
    transaction_type: Optional[str] = None


class TransactionStats(BaseModel):
    """Schema for transaction statistics."""
    total_income: float
    total_expenses: float
    net_amount: float
    transaction_count: int
    category_breakdown: Dict[str, Dict[str, Any]]
    date_range: Dict[str, Optional[str]]


class CategorySuggestion(BaseModel):
    """Schema for ML category suggestions."""
    category_name: str
    confidence: float


class CategoryStats(BaseModel):
    """Schema for category usage statistics."""
    category_id: int
    category_name: str
    category_type: str
    category_color: Optional[str]
    transaction_count: int
    total_amount: float
    last_used: Optional[datetime]


class BudgetStatus(BaseModel):
    """Budget status information for dashboard."""
    id: int
    name: str
    category_name: str
    amount: float
    spent_amount: float
    remaining_amount: float
    progress_percentage: float  
    is_exceeded: bool
    is_near_limit: bool
    days_remaining: int
    status: str

    class Config:
        from_attributes = True


class AgentStatus(BaseModel):
    """Agent emotional state for dashboard."""
    mood_score: float
    current_mood: str
    mood_emoji: str
    personality_type: str
    energy_level: float
    stress_level: float
    needs_attention: bool
    intervention_required: bool
    celebration_pending: bool
    last_mood_change: Optional[datetime]
    mood_change_reason: Optional[str]

    class Config:
        from_attributes = True


class RecentTransaction(BaseModel):
    """Recent transaction for dashboard."""
    id: int
    amount: float
    description: str
    category_name: Optional[str]
    transaction_date: datetime
    is_income: bool
    amount_display: str
    needs_attention: bool

    class Config:
        from_attributes = True


class SpendingByCategory(BaseModel):
    """Spending breakdown by category."""
    category_name: str
    amount: float
    percentage: float
    transaction_count: int
    color: str

    class Config:
        from_attributes = True


class DashboardFilters(BaseModel):
    """Filters for customizing dashboard data."""
    time_period: str = "current_month"  # current_month, last_month, last_3_months, last_year
    include_pending: bool = True
    category_filter: Optional[List[int]] = None
    show_projections: bool = True

    class Config:
        from_attributes = True


class QuickStats(BaseModel):
    """Quick statistics for dashboard widgets."""
    total_balance: float
    this_month_income: float
    this_month_expenses: float
    this_month_savings: float
    goal_completion_eta: Optional[str]
    streak_days: int
    streak_type: Optional[str]

    class Config:
        from_attributes = True 