"""
Pydantic schemas for User model validation and serialization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Base User schema with common fields."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    preferred_currency: str = "EUR"
    language: str = "en"
    timezone: str = "UTC"
    monthly_income: Optional[float] = None
    savings_goal: float = 100000.0

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v.lower()

    @validator('savings_goal')
    def validate_savings_goal(cls, v):
        if v <= 0:
            raise ValueError('Savings goal must be positive')
        if v > 10000000:  # 10 million EUR limit
            raise ValueError('Savings goal too high')
        return v

    @validator('monthly_income')
    def validate_monthly_income(cls, v):
        if v is not None and v < 0:
            raise ValueError('Monthly income cannot be negative')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    preferred_currency: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    monthly_income: Optional[float] = None
    savings_goal: Optional[float] = None

    @validator('savings_goal')
    def validate_savings_goal(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Savings goal must be positive')
            if v > 10000000:
                raise ValueError('Savings goal too high')
        return v


class UserInDB(UserBase):
    """Schema for user data stored in database."""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user data returned in API responses."""
    pass


class UserResponse(User):
    """Schema for user data returned in API responses (alias for User)."""
    pass


class UserProfile(BaseModel):
    """Simplified user profile for public display."""
    id: int
    username: str
    full_name: Optional[str]
    savings_goal: float
    preferred_currency: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics for dashboard."""
    total_transactions: int
    total_income: float
    total_expenses: float
    current_savings: float
    goal_progress_percentage: float
    active_budgets: int
    pending_recommendations: int
    agent_mood_score: float

    class Config:
        from_attributes = True 