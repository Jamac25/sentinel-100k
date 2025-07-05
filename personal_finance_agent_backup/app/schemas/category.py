"""
Pydantic schemas for Category model validation and serialization.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator


class CategoryBase(BaseModel):
    """Base Category schema with common fields."""
    name: str
    description: Optional[str] = None
    is_income: bool = False
    is_essential: bool = False
    color: str = "#6B7280"
    icon: Optional[str] = None
    keywords: Optional[str] = None
    confidence_threshold: float = 0.7

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Category name cannot be empty')
        if len(v) > 100:
            raise ValueError('Category name too long')
        return v.strip().title()

    @validator('color')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color (e.g., #FF0000)')
        return v

    @validator('confidence_threshold')
    def validate_confidence_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence threshold must be between 0.0 and 1.0')
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_income: Optional[bool] = None
    is_essential: Optional[bool] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    keywords: Optional[str] = None
    confidence_threshold: Optional[float] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError('Category name cannot be empty')
            if len(v) > 100:
                raise ValueError('Category name too long')
            return v.strip().title()
        return v


class CategoryInDB(CategoryBase):
    """Schema for category data stored in database."""
    id: int
    parent_id: Optional[int]
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Category(CategoryInDB):
    """Schema for category data returned in API responses."""
    type_label: str

    class Config:
        from_attributes = True


class CategoryResponse(Category):
    """Schema for category data returned in API responses (alias for Category)."""
    pass


class CategoryStats(BaseModel):
    """Category usage statistics."""
    id: int
    name: str
    usage_count: int
    total_amount: float
    average_amount: float
    last_used: Optional[datetime]
    percentage_of_total: float

    class Config:
        from_attributes = True


class CategoryList(BaseModel):
    """List of categories with metadata."""
    categories: List[Category]
    total: int
    income_categories: int
    expense_categories: int
    most_used_category: Optional[str]

    class Config:
        from_attributes = True 