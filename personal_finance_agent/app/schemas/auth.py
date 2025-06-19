"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime


class UserLogin(BaseModel):
    """Schema for user login requests."""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """Schema for user registration requests."""
    email: EmailStr
    name: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserResponse(BaseModel):
    """Schema for user information responses."""
    id: int
    email: str
    name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token responses."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class PasswordChange(BaseModel):
    """Schema for password change requests."""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset requests."""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v 