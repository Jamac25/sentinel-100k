"""
Category management API routes for organizing and managing transaction categories.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from app.schemas import CategoryResponse, CategoryCreate, CategoryUpdate, CategoryStats
from app.models import Category, Transaction, User
from app.db.init_db import get_db
from app.api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=None)
async def list_categories(category_type=Query(None, description="Filter by type (income/expense)"), include_stats=Query(False, description="Include usage statistics"), current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    List all available categories.
    
    Categories are shared across all users but can include personalized statistics.
    """
    try:
        # Build query
        query = db.query(Category)
        
        if category_type:
            query = query.filter(Category.type == category_type)
        
        categories = query.order_by(Category.name).all()
        
        result = []
        for category in categories:
            # Get usage statistics if requested
            usage_count = 0
            last_used = None
            
            if include_stats:
                usage_stats = db.query(
                    func.count(Transaction.id).label('count'),
                    func.max(Transaction.transaction_date).label('last_used')
                ).filter(
                    Transaction.category_id == category.id,
                    Transaction.user_id == current_user.id
                ).first()
                
                usage_count = usage_stats.count if usage_stats.count else 0
                last_used = usage_stats.last_used
            
            result.append(CategoryResponse(
                id=category.id,
                name=category.name,
                type=category.type,
                color=category.color,
                icon=category.icon,
                description=category.description,
                ml_keywords=category.ml_keywords,
                usage_count=usage_count,
                last_used=last_used,
                created_at=category.created_at,
                updated_at=category.updated_at
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.get("/{category_id}", response_model=None)
async def get_category(category_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get a specific category by ID with usage statistics.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Get usage statistics for current user
        usage_stats = db.query(
            func.count(Transaction.id).label('count'),
            func.max(Transaction.transaction_date).label('last_used')
        ).filter(
            Transaction.category_id == category.id,
            Transaction.user_id == current_user.id
        ).first()
        
        usage_count = usage_stats.count if usage_stats.count else 0
        last_used = usage_stats.last_used
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            type=category.type,
            color=category.color,
            icon=category.icon,
            description=category.description,
            ml_keywords=category.ml_keywords,
            usage_count=usage_count,
            last_used=last_used,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(category_data, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Create a new custom category.
    
    Note: In a full implementation, this might be restricted to admin users
    or create user-specific categories.
    """
    try:
        # Check if category name already exists
        existing = db.query(Category).filter(Category.name == category_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        # Create category
        category = Category(
            name=category_data.name,
            type=category_data.type,
            color=category_data.color,
            icon=category_data.icon,
            description=category_data.description,
            ml_keywords=category_data.ml_keywords
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        logger.info(f"Category created: {category.id} by user {current_user.id}")
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            type=category.type,
            color=category.color,
            icon=category.icon,
            description=category.description,
            ml_keywords=category.ml_keywords,
            usage_count=0,
            last_used=None,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )


@router.put("/{category_id}", response_model=None)
async def update_category(category_id, category_data, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Update a category.
    
    Note: In a full implementation, this might be restricted to admin users
    or only allow updates to user-created categories.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Update fields
        if category_data.name is not None:
            # Check name uniqueness
            existing = db.query(Category).filter(
                Category.name == category_data.name,
                Category.id != category_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists"
                )
            category.name = category_data.name
        
        if category_data.type is not None:
            category.type = category_data.type
        
        if category_data.color is not None:
            category.color = category_data.color
        
        if category_data.icon is not None:
            category.icon = category_data.icon
        
        if category_data.description is not None:
            category.description = category_data.description
        
        if category_data.ml_keywords is not None:
            category.ml_keywords = category_data.ml_keywords
        
        db.commit()
        db.refresh(category)
        
        logger.info(f"Category {category_id} updated by user {current_user.id}")
        
        # Get usage statistics
        usage_stats = db.query(
            func.count(Transaction.id).label('count'),
            func.max(Transaction.transaction_date).label('last_used')
        ).filter(
            Transaction.category_id == category.id,
            Transaction.user_id == current_user.id
        ).first()
        
        usage_count = usage_stats.count if usage_stats.count else 0
        last_used = usage_stats.last_used
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            type=category.type,
            color=category.color,
            icon=category.icon,
            description=category.description,
            ml_keywords=category.ml_keywords,
            usage_count=usage_count,
            last_used=last_used,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Delete a category.
    
    Note: This will fail if there are transactions using this category.
    In a production system, you might want to reassign transactions first.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check if category is in use
        transaction_count = db.query(Transaction).filter(
            Transaction.category_id == category_id
        ).count()
        
        if transaction_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category with {transaction_count} associated transactions"
            )
        
        db.delete(category)
        db.commit()
        
        logger.info(f"Category {category_id} deleted by user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )


@router.get("/stats/usage", response_model=None)
async def get_category_usage_stats(category_type=Query(None, description="Filter by type (income/expense)"), limit=Query(10, ge=1, le=50, description="Number of top categories to return"), current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get category usage statistics for the current user.
    
    Returns the most used categories with transaction counts and amounts.
    """
    try:
        # Build query
        query = db.query(
            Category.id,
            Category.name,
            Category.type,
            Category.color,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(func.abs(Transaction.amount)).label('total_amount'),
            func.max(Transaction.transaction_date).label('last_used')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == current_user.id
        ).group_by(
            Category.id, Category.name, Category.type, Category.color
        )
        
        if category_type:
            query = query.filter(Category.type == category_type)
        
        results = query.order_by(
            func.count(Transaction.id).desc()
        ).limit(limit).all()
        
        return [
            CategoryStats(
                category_id=result.id,
                category_name=result.name,
                category_type=result.type,
                category_color=result.color,
                transaction_count=result.transaction_count,
                total_amount=float(result.total_amount) if result.total_amount else 0.0,
                last_used=result.last_used
            )
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Failed to get category usage stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category statistics"
        )


@router.get("/search/suggest", response_model=None)
async def suggest_categories(query=Query(..., min_length=2, description="Search query for category suggestions"), transaction_type=Query(None, description="Filter by transaction type"), limit=Query(5, ge=1, le=20, description="Maximum number of suggestions"), current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get category suggestions based on search query.
    
    Searches category names, descriptions, and ML keywords.
    """
    try:
        # Build search query
        search_term = f"%{query}%"
        
        category_query = db.query(Category).filter(
            or_(
                Category.name.ilike(search_term),
                Category.description.ilike(search_term),
                Category.ml_keywords.ilike(search_term)
            )
        )
        
        if transaction_type:
            category_query = category_query.filter(Category.type == transaction_type)
        
        categories = category_query.limit(limit).all()
        
        return [
            CategoryResponse(
                id=category.id,
                name=category.name,
                type=category.type,
                color=category.color,
                icon=category.icon,
                description=category.description,
                ml_keywords=category.ml_keywords,
                usage_count=0,  # Not calculated for suggestions
                last_used=None,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            for category in categories
        ]
        
    except Exception as e:
        logger.error(f"Failed to suggest categories for query '{query}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get category suggestions"
        )


@router.get("/popular/recommendations", response_model=None)
async def get_popular_categories(category_type=Query(None, description="Filter by type (income/expense)"), limit=Query(10, ge=1, le=20, description="Number of categories to return"), current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get popular category recommendations for the user.
    
    Returns categories that are commonly used by the current user or generally popular.
    """
    try:
        # Get user's most used categories
        user_categories = db.query(
            Category.id,
            func.count(Transaction.id).label('usage_count')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == current_user.id
        ).group_by(Category.id).subquery()
        
        # Build main query
        query = db.query(Category).outerjoin(
            user_categories, Category.id == user_categories.c.id
        )
        
        if category_type:
            query = query.filter(Category.type == category_type)
        
        # Order by user usage, then by category name
        categories = query.order_by(
            user_categories.c.usage_count.desc().nullslast(),
            Category.name
        ).limit(limit).all()
        
        result = []
        for category in categories:
            # Get actual usage count
            usage_count = db.query(func.count(Transaction.id)).filter(
                Transaction.category_id == category.id,
                Transaction.user_id == current_user.id
            ).scalar() or 0
            
            result.append(CategoryResponse(
                id=category.id,
                name=category.name,
                type=category.type,
                color=category.color,
                icon=category.icon,
                description=category.description,
                ml_keywords=category.ml_keywords,
                usage_count=usage_count,
                last_used=None,  # Not calculated for recommendations
                created_at=category.created_at,
                updated_at=category.updated_at
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get popular categories for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get popular categories"
        )


@router.post("/merge", response_model=None)
async def merge_categories(source_category_id, target_category_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    # ... existing code ...
    pass


@router.post("/reassign", response_model=None)
async def reassign_transactions(old_category_id, new_category_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    # ... existing code ...
    pass


@router.post("/initialize/default", response_model=None)
async def initialize_default_categories(db=Depends(get_db)):
    # ... existing code ...
    pass 