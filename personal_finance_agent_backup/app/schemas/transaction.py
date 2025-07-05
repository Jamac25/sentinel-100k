"""
Pydantic schemas for Transaction model validation and serialization.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator
from app.models.transaction import TransactionStatus, TransactionSource


class TransactionBase(BaseModel):
    """Base Transaction schema with common fields."""
    amount: float
    description: str
    transaction_date: datetime
    is_income: bool = False
    merchant: Optional[str] = None
    location: Optional[str] = None
    reference_number: Optional[str] = None
    account: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError('Transaction amount cannot be zero')
        if abs(v) > 1000000:  # 1 million EUR limit
            raise ValueError('Transaction amount too high')
        return round(abs(v), 2)  # Always store as positive, use is_income flag

    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Description cannot be empty')
        if len(v) > 500:
            raise ValueError('Description too long')
        return v.strip()


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    category_id: Optional[int] = None
    source: TransactionSource = TransactionSource.MANUAL
    raw_text: Optional[str] = None

    @validator('category_id')
    def validate_category_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Category ID must be positive')
        return v


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""
    amount: Optional[float] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    is_income: Optional[bool] = None
    category_id: Optional[int] = None
    merchant: Optional[str] = None
    location: Optional[str] = None
    reference_number: Optional[str] = None
    account: Optional[str] = None
    user_verified: Optional[bool] = None
    needs_attention: Optional[bool] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v == 0:
                raise ValueError('Transaction amount cannot be zero')
            if abs(v) > 1000000:
                raise ValueError('Transaction amount too high')
            return round(abs(v), 2)
        return v


class CategoryUpdate(BaseModel):
    """Schema for updating transaction category (for corrections)."""
    category_id: int
    correction_reason: Optional[str] = None

    @validator('category_id')
    def validate_category_id(cls, v):
        if v <= 0:
            raise ValueError('Category ID must be positive')
        return v


class TransactionInDB(TransactionBase):
    """Schema for transaction data stored in database."""
    id: int
    user_id: int
    category_id: Optional[int]
    document_id: Optional[int]
    status: TransactionStatus
    source: TransactionSource
    confidence_score: Optional[float]
    processing_notes: Optional[str]
    user_verified: bool
    needs_attention: bool
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class Transaction(TransactionInDB):
    """Schema for transaction data returned in API responses."""
    # Include related models when needed
    category_name: Optional[str] = None
    amount_display: str
    is_processed: bool
    needs_categorization: bool

    class Config:
        from_attributes = True


class TransactionSummary(BaseModel):
    """Summary statistics for transactions."""
    total_transactions: int
    total_income: float
    total_expenses: float
    net_amount: float
    average_transaction: float
    largest_expense: float
    largest_income: float
    most_common_category: Optional[str]
    uncategorized_count: int

    class Config:
        from_attributes = True


class TransactionList(BaseModel):
    """Paginated list of transactions."""
    transactions: List[Transaction]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


class TransactionFilters(BaseModel):
    """Filters for transaction queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[int] = None
    is_income: Optional[bool] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    merchant: Optional[str] = None
    status: Optional[TransactionStatus] = None
    needs_attention: Optional[bool] = None
    search: Optional[str] = None

    @validator('min_amount', 'max_amount')
    def validate_amounts(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount filters must be positive')
        return v


class TransactionResponse(Transaction):
    """Schema for transaction data returned in API responses (alias for Transaction)."""
    pass


class TransactionWithCategory(Transaction):
    """Schema for transaction with category details (alias for Transaction)."""
    pass 