"""
Dashboard API routes for financial analytics, summaries, and insights.
"""
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, and_, extract
from app.schemas import DashboardSummary, MonthlyTrend, CategoryBreakdown, GoalProgress
from app.models import Transaction, Category, User, Goal, AgentState
from app.db.init_db import get_db
from app.api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=None)
async def get_dashboard_summary(period_days=Query(30, ge=1, le=365, description="Number of days to include in summary"), current_user=Depends(get_current_user), db=Depends(get_db)) -> None:
    """
    Get comprehensive dashboard summary for the specified period.
    
    Includes financial metrics, trends, and progress towards goals.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get transactions for the period
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).all()
        
        # Calculate basic metrics
        total_income = sum(abs(txn.amount) for txn in transactions if txn.amount < 0)
        total_expenses = sum(txn.amount for txn in transactions if txn.amount > 0)
        net_amount = total_income - total_expenses
        transaction_count = len(transactions)
        
        # Calculate average daily spending
        avg_daily_spending = total_expenses / period_days if period_days > 0 else 0
        
        # Get category breakdown
        category_stats = {}
        for txn in transactions:
            if txn.category:
                category_name = txn.category.name
                if category_name not in category_stats:
                    category_stats[category_name] = {
                        "amount": 0,
                        "count": 0,
                        "type": txn.category.type,
                        "color": txn.category.color
                    }
                
                category_stats[category_name]["amount"] += abs(txn.amount)
                category_stats[category_name]["count"] += 1
        
        # Get monthly trends (last 6 months)
        monthly_trends = await _get_monthly_trends(current_user.id, db)
        
        # Get goal progress
        goal_progress = await _get_goal_progress(current_user.id, db)
        
        # Get agent state
        agent_state = db.query(AgentState).filter(
            AgentState.user_id == current_user.id
        ).first()
        
        agent_mood = agent_state.mood_score if agent_state else 50
        agent_message = _generate_agent_message(net_amount, agent_mood, goal_progress)
        
        # Previous period comparison
        prev_start = start_date - timedelta(days=period_days)
        prev_transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= prev_start,
            Transaction.transaction_date < start_date
        ).all()
        
        prev_expenses = sum(txn.amount for txn in prev_transactions if txn.amount > 0)
        expense_change = ((total_expenses - prev_expenses) / prev_expenses * 100) if prev_expenses > 0 else 0
        
        return DashboardSummary(
            period_days=period_days,
            total_income=total_income,
            total_expenses=total_expenses,
            net_amount=net_amount,
            transaction_count=transaction_count,
            avg_daily_spending=avg_daily_spending,
            expense_change_percent=expense_change,
            category_breakdown=category_stats,
            monthly_trends=monthly_trends,
            goal_progress=goal_progress,
            agent_mood=agent_mood,
            agent_message=agent_message,
            top_categories=[
                {
                    "name": name,
                    "amount": stats["amount"],
                    "percentage": (stats["amount"] / total_expenses * 100) if total_expenses > 0 else 0
                }
                for name, stats in sorted(
                    category_stats.items(),
                    key=lambda x: x[1]["amount"],
                    reverse=True
                )[:5]
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to get dashboard summary for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )


@router.get("/trends/monthly", response_model=None)
async def get_monthly_trends(months=Query(12, ge=3, le=24, description="Number of months to include"), current_user=Depends(get_current_user), db=Depends(get_db)) -> None:
    """
    Get monthly financial trends for the specified number of months.
    """
    try:
        return await _get_monthly_trends(current_user.id, db, months)
        
    except Exception as e:
        logger.error(f"Failed to get monthly trends for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monthly trends"
        )


@router.get("/categories/breakdown", response_model=None)
async def get_category_breakdown(period_days=Query(30, ge=1, le=365, description="Number of days to analyze"), transaction_type=Query(None, description="Filter by type (income/expense)"), current_user=Depends(get_current_user), db=Depends(get_db)) -> None:
    """
    Get detailed category breakdown for spending analysis.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Build query
        query = db.query(
            Category.id,
            Category.name,
            Category.type,
            Category.color,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(func.abs(Transaction.amount)).label('total_amount'),
            func.avg(func.abs(Transaction.amount)).label('avg_amount'),
            func.max(Transaction.transaction_date).label('last_transaction')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(
            Category.id, Category.name, Category.type, Category.color
        )
        
        if transaction_type:
            query = query.filter(Category.type == transaction_type)
        
        results = query.order_by(
            func.sum(func.abs(Transaction.amount)).desc()
        ).all()
        
        # Calculate total for percentages
        total_amount = sum(result.total_amount for result in results)
        
        return [
            CategoryBreakdown(
                category_id=result.id,
                category_name=result.name,
                category_type=result.type,
                category_color=result.color,
                total_amount=float(result.total_amount),
                transaction_count=result.transaction_count,
                average_amount=float(result.avg_amount),
                percentage=(result.total_amount / total_amount * 100) if total_amount > 0 else 0,
                last_transaction=result.last_transaction
            )
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Failed to get category breakdown for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category breakdown"
        )


@router.get("/goals/progress", response_model=None)
async def get_all_goals_progress(current_user=Depends(get_current_user), db=Depends(get_db)) -> None:
    """
    Get progress towards all user goals.
    """
    try:
        return await _get_goal_progress(current_user.id, db)
        
    except Exception as e:
        logger.error(f"Failed to get goal progress for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve goal progress"
        )


@router.get("/spending/forecast", response_model=None)
async def get_spending_forecast(forecast_days=Query(30, ge=7, le=90, description="Number of days to forecast"), current_user=Depends(get_current_user), db=Depends(get_db)) -> None:
    """
    Get spending forecast based on historical data.
    
    Uses simple linear regression on recent spending patterns.
    """
    try:
        # Get last 90 days of data for forecasting
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # Get daily spending amounts
        daily_spending = db.query(
            func.date(Transaction.transaction_date).label('date'),
            func.sum(Transaction.amount).label('daily_amount')
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.amount > 0  # Only expenses
        ).group_by(
            func.date(Transaction.transaction_date)
        ).order_by(
            func.date(Transaction.transaction_date)
        ).all()
        
        if len(daily_spending) < 7:
            return {
                "forecast_days": forecast_days,
                "predicted_total": 0,
                "daily_average": 0,
                "confidence": "low",
                "message": "Insufficient data for accurate forecasting"
            }
        
        # Calculate simple average
        total_spending = sum(day.daily_amount for day in daily_spending)
        avg_daily = total_spending / len(daily_spending)
        
        # Simple forecast
        predicted_total = avg_daily * forecast_days
        
        # Calculate trend (simple slope)
        if len(daily_spending) >= 14:
            recent_avg = sum(day.daily_amount for day in daily_spending[-7:]) / 7
            older_avg = sum(day.daily_amount for day in daily_spending[-14:-7]) / 7
            trend = "increasing" if recent_avg > older_avg else "decreasing"
        else:
            trend = "stable"
        
        confidence = "high" if len(daily_spending) >= 30 else "medium"
        
        return {
            "forecast_days": forecast_days,
            "predicted_total": round(predicted_total, 2),
            "daily_average": round(avg_daily, 2),
            "trend": trend,
            "confidence": confidence,
            "historical_days": len(daily_spending),
            "message": f"Based on {len(daily_spending)} days of spending data"
        }
        
    except Exception as e:
        logger.error(f"Failed to get spending forecast for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate spending forecast"
        )


@router.get("/insights/smart", response_model=None)
async def get_smart_insights(current_user=Depends(get_current_user), db=Depends(get_db)) -> None:
    """
    Get AI-powered smart insights about spending patterns and recommendations.
    """
    try:
        insights = []
        
        # Get last 30 days of transactions
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start_date
        ).all()
        
        if not transactions:
            return {
                "insights": [],
                "message": "No recent transactions to analyze"
            }
        
        # Insight 1: Highest spending category
        category_totals = {}
        for txn in transactions:
            if txn.category and txn.amount > 0:
                category_name = txn.category.name
                category_totals[category_name] = category_totals.get(category_name, 0) + txn.amount
        
        if category_totals:
            top_category = max(category_totals.items(), key=lambda x: x[1])
            insights.append({
                "type": "spending_pattern",
                "title": "Highest Spending Category",
                "message": f"You spent €{top_category[1]:.2f} on {top_category[0]} this month",
                "category": top_category[0],
                "amount": top_category[1]
            })
        
        # Insight 2: Spending frequency
        weekend_spending = sum(txn.amount for txn in transactions 
                             if txn.amount > 0 and txn.transaction_date.weekday() >= 5)
        weekday_spending = sum(txn.amount for txn in transactions 
                             if txn.amount > 0 and txn.transaction_date.weekday() < 5)
        
        if weekend_spending > weekday_spending:
            insights.append({
                "type": "behavior",
                "title": "Weekend Spending Pattern",
                "message": f"You tend to spend more on weekends (€{weekend_spending:.2f}) than weekdays (€{weekday_spending:.2f})",
                "recommendation": "Consider planning weekend activities with a budget"
            })
        
        # Insight 3: Large transactions
        large_transactions = [txn for txn in transactions if txn.amount > 100]
        if large_transactions:
            avg_large = sum(txn.amount for txn in large_transactions) / len(large_transactions)
            insights.append({
                "type": "alert",
                "title": "Large Transactions",
                "message": f"You had {len(large_transactions)} transactions over €100, averaging €{avg_large:.2f}",
                "count": len(large_transactions)
            })
        
        # Insight 4: Goal progress
        goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
        for goal in goals:
            progress_percent = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            if progress_percent >= 75:
                insights.append({
                    "type": "achievement",
                    "title": "Goal Progress",
                    "message": f"Great job! You're {progress_percent:.1f}% towards your {goal.name} goal",
                    "goal_name": goal.name,
                    "progress": progress_percent
                })
        
        return {
            "insights": insights,
            "analyzed_period": "last 30 days",
            "transaction_count": len(transactions),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get smart insights for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate smart insights"
        )


@router.get("/agent/message", response_model=None)
async def get_agent_message(current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Get a personalized message from the AI agent.
    """
    try:
        agent_state = db.query(AgentState).filter(AgentState.user_id == current_user.id).first()
        mood = agent_state.mood_score if agent_state else 50
        message = _generate_agent_message(0, mood, [])
        return {"message": message, "mood": mood}
    except Exception as e:
        logger.error(f"Failed to get agent message: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent message")


# Helper functions

async def _get_monthly_trends(user_id, db, months=6) -> None:
    """Get monthly trends for the specified number of months."""
    trends = []
    
    for i in range(months):
        # Calculate month start/end dates
        current_date = datetime.now().replace(day=1) - timedelta(days=i*30)
        month_start = current_date.replace(day=1)
        
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)
        
        month_end = next_month - timedelta(days=1)
        
        # Get transactions for the month
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= month_start,
            Transaction.transaction_date <= month_end
        ).all()
        
        income = sum(abs(txn.amount) for txn in transactions if txn.amount < 0)
        expenses = sum(txn.amount for txn in transactions if txn.amount > 0)
        
        trends.insert(0, MonthlyTrend(  # Insert at beginning to maintain chronological order
            month=month_start.strftime("%Y-%m"),
            month_name=month_start.strftime("%B %Y"),
            income=income,
            expenses=expenses,
            net_amount=income - expenses,
            transaction_count=len(transactions)
        ))
    
    return trends


async def _get_goal_progress(user_id, db):
    """Get progress for all user goals."""
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    
    progress_list = []
    for goal in goals:
        progress_percent = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        
        # Calculate days remaining
        days_remaining = (goal.target_date - datetime.now().date()).days if goal.target_date else None
        
        # Determine status
        if progress_percent >= 100:
            status = "completed"
        elif days_remaining and days_remaining < 0:
            status = "overdue"
        elif progress_percent >= 75:
            status = "on_track"
        else:
            status = "behind"
        
        progress_list.append(GoalProgress(
            goal_id=goal.id,
            goal_name=goal.name,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            progress_percent=progress_percent,
            target_date=goal.target_date,
            days_remaining=days_remaining,
            status=status
        ))
    
    return progress_list


def _generate_agent_message(net_amount, mood_score, goal_progress):
    """Generate a personalized message from the AI agent based on financial status."""
    if mood_score >= 80:
        base_messages = [
            "Excellent work on your finances! 🎉",
            "You're doing fantastic with your money management! ⭐",
            "Keep up the amazing financial progress! 🚀"
        ]
    elif mood_score >= 60:
        base_messages = [
            "Good job managing your finances! 👍",
            "You're on the right track! 💪",
            "Steady progress with your money! 📈"
        ]
    elif mood_score >= 40:
        base_messages = [
            "Let's work on improving your financial health 💡",
            "There's room for improvement in your spending 📊",
            "Consider reviewing your budget strategy 🤔"
        ]
    else:
        base_messages = [
            "I'm here to help you get back on track! 🎯",
            "Let's create a plan to improve your finances 📋",
            "Don't worry, we can turn this around together! 💪"
        ]
    
    # Add goal-specific messages
    completed_goals = [g for g in goal_progress if g.status == "completed"]
    if completed_goals:
        return f"{base_messages[0]} You've completed {len(completed_goals)} goals!"
    
    if net_amount > 0:
        return f"{base_messages[0]} You saved €{net_amount:.2f} this period!"
    
    return base_messages[0] 