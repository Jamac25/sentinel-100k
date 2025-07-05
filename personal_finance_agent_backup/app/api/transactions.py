"""
Transaction management API routes for CRUD operations, categorization, and filtering.
"""
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import and_, or_, func
from app.schemas import (
    TransactionResponse, TransactionCreate, TransactionUpdate, 
    TransactionFilters, TransactionStats, CategorySuggestion
)
from app.models import Transaction, Category, User, CategoryCorrection
from app.services import TransactionCategorizationService
from app.db.init_db import get_db
from app.api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["transactions"])
categorization_service = TransactionCategorizationService()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_data, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Create a new transaction.
    
    Automatically categorizes the transaction using ML if no category is provided.
    """
    try:
        # Auto-categorize if no category provided
        category_id = transaction_data.category_id
        ml_confidence = 0.0
        
        if not category_id and transaction_data.description:
            categorization = categorization_service.categorize_transaction(
                description=transaction_data.description,
                amount=float(transaction_data.amount),
                merchant=transaction_data.merchant_name,
                user_id=current_user.id,
                db=db
            )
            category_id = categorization.get("category_id")
            ml_confidence = categorization.get("confidence", 0.0)
        
        # Create transaction
        transaction = Transaction(
            amount=transaction_data.amount,
            description=transaction_data.description,
            merchant_name=transaction_data.merchant_name,
            transaction_date=transaction_data.transaction_date or datetime.now(),
            category_id=category_id,
            ml_confidence=ml_confidence,
            user_id=current_user.id,
            type=transaction_data.type,
            status=transaction_data.status or "completed"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Transaction created: {transaction.id} by user {current_user.id}")
        
        return TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            description=transaction.description,
            merchant_name=transaction.merchant_name,
            transaction_date=transaction.transaction_date,
            category_id=transaction.category_id,
            category_name=transaction.category.name if transaction.category else None,
            ml_confidence=transaction.ml_confidence,
            type=transaction.type,
            status=transaction.status,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction"
        )


@router.get("/", response_model=None)
async def list_transactions(skip=Query(0, ge=0), limit=Query(50, ge=1, le=100), date_from=Query(None), date_to=Query(None), category_id=Query(None), transaction_type=Query(None), min_amount=Query(None), max_amount=Query(None), search=Query(None), current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    List user's transactions with advanced filtering options.
    
    Supports pagination, date range filtering, category filtering, and text search.
    """
    try:
        # Build query
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
        
        # Apply filters
        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        
        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)
        
        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.description.ilike(search_term),
                    Transaction.merchant_name.ilike(search_term)
                )
            )
        
        # Execute query with pagination
        transactions = query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
        
        return [
            TransactionResponse(
                id=txn.id,
                amount=txn.amount,
                description=txn.description,
                merchant_name=txn.merchant_name,
                transaction_date=txn.transaction_date,
                category_id=txn.category_id,
                category_name=txn.category.name if txn.category else None,
                ml_confidence=txn.ml_confidence,
                type=txn.type,
                status=txn.status,
                created_at=txn.created_at,
                updated_at=txn.updated_at
            )
            for txn in transactions
        ]
        
    except Exception as e:
        logger.error(f"Failed to list transactions for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get a specific transaction by ID.
    """
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            description=transaction.description,
            merchant_name=transaction.merchant_name,
            transaction_date=transaction.transaction_date,
            category_id=transaction.category_id,
            category_name=transaction.category.name if transaction.category else None,
            ml_confidence=transaction.ml_confidence,
            type=transaction.type,
            status=transaction.status,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction"
        )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id, transaction_data, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Update a transaction.
    
    If the category is changed, stores the correction for ML learning.
    """
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Store original category for correction tracking
        original_category_id = transaction.category_id
        
        # Update fields
        if transaction_data.amount is not None:
            transaction.amount = transaction_data.amount
        
        if transaction_data.description is not None:
            transaction.description = transaction_data.description
        
        if transaction_data.merchant_name is not None:
            transaction.merchant_name = transaction_data.merchant_name
        
        if transaction_data.transaction_date is not None:
            transaction.transaction_date = transaction_data.transaction_date
        
        if transaction_data.category_id is not None:
            transaction.category_id = transaction_data.category_id
            
            # Store correction if category changed
            if original_category_id != transaction_data.category_id:
                categorization_service.learn_from_correction(
                    transaction_id=transaction.id,
                    correct_category_id=transaction_data.category_id,
                    user_id=current_user.id,
                    db=db
                )
        
        if transaction_data.type is not None:
            transaction.type = transaction_data.type
        
        if transaction_data.status is not None:
            transaction.status = transaction_data.status
        
        transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Transaction {transaction_id} updated by user {current_user.id}")
        
        return TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            description=transaction.description,
            merchant_name=transaction.merchant_name,
            transaction_date=transaction.transaction_date,
            category_id=transaction.category_id,
            category_name=transaction.category.name if transaction.category else None,
            ml_confidence=transaction.ml_confidence,
            type=transaction.type,
            status=transaction.status,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update transaction"
        )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Delete a transaction.
    """
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        db.delete(transaction)
        db.commit()
        
        logger.info(f"Transaction {transaction_id} deleted by user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete transaction"
        )


@router.get("/stats/summary", response_model=TransactionStats)
async def get_transaction_stats(date_from=Query(None), date_to=Query(None), current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get transaction statistics for the current user.
    
    Returns income, expenses, and category breakdowns for the specified date range.
    """
    try:
        # Build base query
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
        
        # Apply date filters
        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        
        transactions = query.all()
        
        # Calculate statistics
        total_income = sum(abs(txn.amount) for txn in transactions if txn.amount < 0)
        total_expenses = sum(txn.amount for txn in transactions if txn.amount > 0)
        net_amount = total_income - total_expenses
        transaction_count = len(transactions)
        
        # Category breakdown
        category_stats = {}
        for txn in transactions:
            if txn.category:
                category_name = txn.category.name
                if category_name not in category_stats:
                    category_stats[category_name] = {"count": 0, "amount": 0}
                
                category_stats[category_name]["count"] += 1
                category_stats[category_name]["amount"] += abs(txn.amount)
        
        return TransactionStats(
            total_income=total_income,
            total_expenses=total_expenses,
            net_amount=net_amount,
            transaction_count=transaction_count,
            category_breakdown=category_stats,
            date_range={
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get transaction stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction statistics"
        )


@router.post("/{transaction_id}/categorize", response_model=None)
async def recategorize_transaction(transaction_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Re-categorize a transaction using the latest ML model.
    
    Useful for improving categorization of existing transactions.
    """
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Get new categorization
        categorization = categorization_service.categorize_transaction(
            description=transaction.description or "",
            amount=float(transaction.amount),
            merchant=transaction.merchant_name,
            user_id=current_user.id,
            db=db
        )
        
        # Store original category
        original_category_id = transaction.category_id
        
        # Update transaction
        transaction.category_id = categorization.get("category_id")
        transaction.ml_confidence = categorization.get("confidence", 0.0)
        transaction.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Transaction {transaction_id} re-categorized by user {current_user.id}")
        
        return {
            "transaction_id": transaction_id,
            "original_category_id": original_category_id,
            "new_category_id": transaction.category_id,
            "confidence": transaction.ml_confidence,
            "suggestions": categorization.get("all_predictions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to re-categorize transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to re-categorize transaction"
        )


@router.get("/{transaction_id}/category-suggestions", response_model=None)
async def get_category_suggestions(transaction_id, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get category suggestions for a specific transaction.
    
    Returns ML-powered suggestions for categorizing the transaction.
    """
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Get suggestions
        suggestions = categorization_service.get_category_suggestions(
            description=transaction.description or "",
            merchant=transaction.merchant_name,
            top_k=5
        )
        
        return [
            CategorySuggestion(
                category_name=suggestion["category_name"],
                confidence=suggestion["confidence"]
            )
            for suggestion in suggestions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get category suggestions for transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get category suggestions"
        )


@router.post("/bulk-categorize", response_model=None)
async def bulk_categorize_transactions(limit=Query(100, ge=1, le=500), current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Bulk categorize uncategorized transactions.
    
    Processes transactions without categories using the ML model.
    """
    try:
        # Find uncategorized transactions
        uncategorized = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id.is_(None)
        ).limit(limit).all()
        
        categorized_count = 0
        failed_count = 0
        
        for transaction in uncategorized:
            try:
                # Categorize transaction
                categorization = categorization_service.categorize_transaction(
                    description=transaction.description or "",
                    amount=float(transaction.amount),
                    merchant=transaction.merchant_name,
                    user_id=current_user.id,
                    db=db
                )
                
                # Update transaction
                transaction.category_id = categorization.get("category_id")
                transaction.ml_confidence = categorization.get("confidence", 0.0)
                transaction.updated_at = datetime.utcnow()
                
                categorized_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to categorize transaction {transaction.id}: {e}")
                failed_count += 1
        
        db.commit()
        
        logger.info(f"Bulk categorization completed for user {current_user.id}: {categorized_count} success, {failed_count} failed")
        
        return {
            "processed": len(uncategorized),
            "categorized": categorized_count,
            "failed": failed_count,
            "success_rate": (categorized_count / len(uncategorized) * 100) if uncategorized else 0
        }
        
    except Exception as e:
        logger.error(f"Bulk categorization failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk categorize transactions"
        ) 