"""
Sentinel Predictive Budget™ - ML-based Budget Prediction and Optimization
Integrates with LearningEngine, Watchdog, and Scheduler for intelligent budget management
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.category import Category
from ..services.event_bus import EventType, publish_event
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import json
import asyncio
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class BudgetOptimizationLevel(Enum):
    """Budget optimization levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EMERGENCY = "emergency"

@dataclass
class BudgetPrediction:
    """Budget prediction data structure"""
    category_id: int
    category_name: str
    predicted_amount: float
    confidence_score: float
    trend_direction: str  # increasing, decreasing, stable
    risk_level: str  # low, medium, high
    optimization_suggestions: List[str]

@dataclass
class BudgetOptimization:
    """Budget optimization data structure"""
    category_id: int
    category_name: str
    current_budget: float
    optimized_budget: float
    reduction_amount: float
    reduction_percentage: float
    priority: str  # high, medium, low
    reasoning: str

class PredictiveBudget:
    """
    Sentinel Predictive Budget™ - ML-based Budget Prediction
    
    Features:
    - ML-powered expense prediction for next month
    - Automatic budget optimization based on Watchdog risk level
    - Proactive warnings before budget overruns
    - Dynamic category weighting based on behavior patterns
    - Savings potential calculation and optimization suggestions
    """
    
    def __init__(self):
        self.ml_models = {}  # category_id -> RandomForestRegressor
        self.scalers = {}  # category_id -> StandardScaler
        self.prediction_history = {}  # user_id -> List[Dict]
        self.optimization_history = {}  # user_id -> List[Dict]
        self.model_accuracy = {}  # category_id -> float
        
        # Budget optimization rules
        self.optimization_rules = {
            BudgetOptimizationLevel.CONSERVATIVE: {
                "max_reduction": 0.1,  # 10% max reduction
                "priority_categories": ["entertainment", "shopping"],
                "protected_categories": ["groceries", "transportation"]
            },
            BudgetOptimizationLevel.MODERATE: {
                "max_reduction": 0.2,  # 20% max reduction
                "priority_categories": ["entertainment", "shopping", "dining"],
                "protected_categories": ["groceries", "transportation", "utilities"]
            },
            BudgetOptimizationLevel.AGGRESSIVE: {
                "max_reduction": 0.35,  # 35% max reduction
                "priority_categories": ["entertainment", "shopping", "dining", "luxury"],
                "protected_categories": ["groceries", "transportation", "utilities", "health"]
            },
            BudgetOptimizationLevel.EMERGENCY: {
                "max_reduction": 0.5,  # 50% max reduction
                "priority_categories": ["entertainment", "shopping", "dining", "luxury", "non_essential"],
                "protected_categories": ["groceries", "transportation", "utilities", "health", "housing"]
            }
        }
    
    async def generate_next_month_budget(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Generate ML-based budget prediction for next month"""
        try:
            # Get user's transaction history
            transactions = self._get_user_transactions(user_id, db)
            
            if not transactions:
                return {
                    "status": "no_data",
                    "message": "Insufficient transaction data for prediction"
                }
            
            # Prepare features for ML
            features = self._prepare_features(transactions)
            
            # Generate predictions for each category
            predictions = []
            total_predicted = 0.0
            
            for category_id in features.keys():
                prediction = await self._predict_category_expense(
                    user_id, category_id, features[category_id]
                )
                if prediction:
                    predictions.append(prediction)
                    total_predicted += prediction.predicted_amount
            
            # Store prediction history
            if user_id not in self.prediction_history:
                self.prediction_history[user_id] = []
            
            prediction_record = {
                "timestamp": datetime.now().isoformat(),
                "predictions": [self._prediction_to_dict(p) for p in predictions],
                "total_predicted": total_predicted,
                "month": (datetime.now() + timedelta(days=30)).strftime("%Y-%m")
            }
            
            self.prediction_history[user_id].append(prediction_record)
            
            # Publish prediction event
            await publish_event(
                EventType.BUDGET_PREDICTION_UPDATED,
                user_id,
                {
                    "total_predicted": total_predicted,
                    "categories_count": len(predictions),
                    "prediction_month": prediction_record["month"]
                },
                "predictive_budget"
            )
            
            return {
                "status": "success",
                "predictions": [self._prediction_to_dict(p) for p in predictions],
                "total_predicted": total_predicted,
                "prediction_month": prediction_record["month"],
                "confidence_score": np.mean([p.confidence_score for p in predictions]),
                "risk_assessment": self._assess_budget_risk(predictions, total_predicted)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate budget prediction: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_user_transactions(self, user_id: int, db: Session) -> List[Transaction]:
        """Get user's transaction history for ML training"""
        try:
            # Get last 12 months of transactions
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0  # Expenses only
            ).order_by(Transaction.transaction_date).all()
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get user transactions: {e}")
            return []
    
    def _prepare_features(self, transactions: List[Transaction]) -> Dict[int, List[Dict[str, Any]]]:
        """Prepare features for ML prediction"""
        try:
            features = {}
            
            # Group transactions by category
            for transaction in transactions:
                category_id = transaction.category_id or 1  # Default category
                
                if category_id not in features:
                    features[category_id] = []
                
                # Create feature vector for each transaction
                feature_vector = {
                    "amount": transaction.amount,
                    "day_of_week": transaction.transaction_date.weekday(),
                    "day_of_month": transaction.transaction_date.day,
                    "month": transaction.transaction_date.month,
                    "quarter": (transaction.transaction_date.month - 1) // 3 + 1,
                    "is_weekend": transaction.transaction_date.weekday() >= 5,
                    "is_month_end": transaction.transaction_date.day >= 25,
                    "is_month_start": transaction.transaction_date.day <= 5
                }
                
                features[category_id].append(feature_vector)
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to prepare features: {e}")
            return {}
    
    async def _predict_category_expense(self, user_id: int, category_id: int, 
                                      features: List[Dict[str, Any]]) -> Optional[BudgetPrediction]:
        """Predict expense for specific category using ML"""
        try:
            if len(features) < 10:  # Need minimum data for prediction
                return None
            
            # Prepare training data
            X = []
            y = []
            
            # Create monthly aggregates
            monthly_data = {}
            for feature in features:
                month_key = f"{feature['month']}_{feature['quarter']}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "total_amount": 0,
                        "transaction_count": 0,
                        "avg_amount": 0,
                        "weekend_ratio": 0,
                        "month_end_ratio": 0
                    }
                
                monthly_data[month_key]["total_amount"] += feature["amount"]
                monthly_data[month_key]["transaction_count"] += 1
                monthly_data[month_key]["weekend_ratio"] += feature["is_weekend"]
                monthly_data[month_key]["month_end_ratio"] += feature["is_month_end"]
            
            # Calculate averages
            for month_data in monthly_data.values():
                month_data["avg_amount"] = month_data["total_amount"] / month_data["transaction_count"]
                month_data["weekend_ratio"] /= month_data["transaction_count"]
                month_data["month_end_ratio"] /= month_data["transaction_count"]
            
            # Create feature matrix
            for month_key, month_data in monthly_data.items():
                X.append([
                    month_data["transaction_count"],
                    month_data["avg_amount"],
                    month_data["weekend_ratio"],
                    month_data["month_end_ratio"]
                ])
                y.append(month_data["total_amount"])
            
            if len(X) < 3:  # Need at least 3 months of data
                return None
            
            # Train or update ML model
            model = await self._train_category_model(category_id, X, y)
            
            if not model:
                return None
            
            # Make prediction for next month
            next_month_features = self._generate_next_month_features(monthly_data)
            predicted_amount = model.predict([next_month_features])[0]
            
            # Calculate confidence score
            confidence_score = self._calculate_prediction_confidence(model, X, y)
            
            # Determine trend direction
            trend_direction = self._determine_trend_direction(y)
            
            # Determine risk level
            risk_level = self._determine_risk_level(predicted_amount, y)
            
            # Get category name
            category_name = self._get_category_name(category_id)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                predicted_amount, y, risk_level
            )
            
            return BudgetPrediction(
                category_id=category_id,
                category_name=category_name,
                predicted_amount=predicted_amount,
                confidence_score=confidence_score,
                trend_direction=trend_direction,
                risk_level=risk_level,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            logger.error(f"Failed to predict category expense: {e}")
            return None
    
    async def _train_category_model(self, category_id: int, X: List[List[float]], 
                                  y: List[float]) -> Optional[RandomForestRegressor]:
        """Train or update ML model for category"""
        try:
            if len(X) < 3:
                return None
            
            # Initialize model if not exists
            if category_id not in self.ml_models:
                self.ml_models[category_id] = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    max_depth=5
                )
                self.scalers[category_id] = StandardScaler()
            
            # Scale features
            X_scaled = self.scalers[category_id].fit_transform(X)
            
            # Train model
            self.ml_models[category_id].fit(X_scaled, y)
            
            # Calculate model accuracy
            if len(X) >= 4:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.25, random_state=42
                )
                self.ml_models[category_id].fit(X_train, y_train)
                accuracy = self.ml_models[category_id].score(X_test, y_test)
                self.model_accuracy[category_id] = max(0, accuracy)
            
            return self.ml_models[category_id]
            
        except Exception as e:
            logger.error(f"Failed to train category model: {e}")
            return None
    
    def _generate_next_month_features(self, monthly_data: Dict[str, Dict[str, Any]]) -> List[float]:
        """Generate features for next month prediction"""
        try:
            if not monthly_data:
                return [1, 100, 0.3, 0.2]  # Default features
            
            # Calculate averages from historical data
            total_transactions = sum(d["transaction_count"] for d in monthly_data.values())
            avg_amount = sum(d["avg_amount"] for d in monthly_data.values()) / len(monthly_data)
            avg_weekend_ratio = sum(d["weekend_ratio"] for d in monthly_data.values()) / len(monthly_data)
            avg_month_end_ratio = sum(d["month_end_ratio"] for d in monthly_data.values()) / len(monthly_data)
            
            # Predict next month based on trends
            recent_data = list(monthly_data.values())[-3:]  # Last 3 months
            if len(recent_data) >= 2:
                # Simple trend calculation
                recent_avg = sum(d["transaction_count"] for d in recent_data) / len(recent_data)
                predicted_transactions = recent_avg * 1.05  # 5% growth assumption
            else:
                predicted_transactions = total_transactions / len(monthly_data)
            
            return [
                predicted_transactions,
                avg_amount,
                avg_weekend_ratio,
                avg_month_end_ratio
            ]
            
        except Exception as e:
            logger.error(f"Failed to generate next month features: {e}")
            return [1, 100, 0.3, 0.2]
    
    def _calculate_prediction_confidence(self, model: RandomForestRegressor, 
                                       X: List[List[float]], y: List[float]) -> float:
        """Calculate confidence score for prediction"""
        try:
            if len(X) < 3:
                return 0.5
            
            # Use model accuracy as confidence
            accuracy = self.model_accuracy.get(id(model), 0.7)
            
            # Adjust based on data consistency
            if len(y) >= 3:
                variance = np.var(y)
                mean = np.mean(y)
                coefficient_of_variation = np.sqrt(variance) / mean if mean > 0 else 1
                
                # Higher confidence for more consistent data
                consistency_factor = max(0.1, 1 - coefficient_of_variation)
                confidence = accuracy * consistency_factor
            else:
                confidence = accuracy * 0.8
            
            return min(max(confidence, 0.1), 0.95)
            
        except Exception as e:
            logger.error(f"Failed to calculate confidence: {e}")
            return 0.5
    
    def _determine_trend_direction(self, y: List[float]) -> str:
        """Determine trend direction from historical data"""
        try:
            if len(y) < 3:
                return "stable"
            
            # Calculate trend using linear regression
            x = list(range(len(y)))
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > np.mean(y) * 0.1:  # 10% threshold
                return "increasing"
            elif slope < -np.mean(y) * 0.1:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Failed to determine trend: {e}")
            return "stable"
    
    def _determine_risk_level(self, predicted_amount: float, historical_amounts: List[float]) -> str:
        """Determine risk level for prediction"""
        try:
            if not historical_amounts:
                return "medium"
            
            mean_amount = np.mean(historical_amounts)
            std_amount = np.std(historical_amounts)
            
            if std_amount == 0:
                return "low"
            
            z_score = abs(predicted_amount - mean_amount) / std_amount
            
            if z_score < 1:
                return "low"
            elif z_score < 2:
                return "medium"
            else:
                return "high"
                
        except Exception as e:
            logger.error(f"Failed to determine risk level: {e}")
            return "medium"
    
    def _get_category_name(self, category_id: int) -> str:
        """Get category name by ID"""
        try:
            # This would query the database
            # For now, return mock names
            category_names = {
                1: "Ruoka",
                2: "Kuljetus",
                3: "Viihde",
                4: "Ostokset",
                5: "Laskut",
                6: "Säästöt"
            }
            return category_names.get(category_id, f"Kategoria {category_id}")
        except Exception as e:
            logger.error(f"Failed to get category name: {e}")
            return f"Kategoria {category_id}"
    
    def _generate_optimization_suggestions(self, predicted_amount: float, 
                                         historical_amounts: List[float], 
                                         risk_level: str) -> List[str]:
        """Generate optimization suggestions"""
        try:
            suggestions = []
            
            if risk_level == "high":
                suggestions.extend([
                    "Harkitse kulujen leikkaamista tässä kategoriassa",
                    "Aseta tiukempi budjetti seuraavalle kuukaudelle",
                    "Seuraa kuluja tarkemmin"
                ])
            
            if predicted_amount > np.mean(historical_amounts) * 1.2:
                suggestions.append("Kulut ovat nousussa - tarkista tarpeellisuus")
            
            if len(historical_amounts) >= 3:
                recent_avg = np.mean(historical_amounts[-3:])
                if predicted_amount > recent_avg * 1.1:
                    suggestions.append("Viimeaikainen trendi on nousussa")
            
            if not suggestions:
                suggestions.append("Kulut ovat tasaisia - hyvä!")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return ["Seuraa kulujasi tarkasti"]
    
    async def optimize_budget(self, user_id: int, risk_level: str, 
                            current_budgets: Dict[int, float]) -> Dict[str, Any]:
        """Optimize budget based on risk level and predictions"""
        try:
            # Get optimization level based on risk
            optimization_level = self._get_optimization_level(risk_level)
            rules = self.optimization_rules[optimization_level]
            
            # Get latest predictions
            latest_prediction = self.prediction_history.get(user_id, [{}])[-1]
            predictions = latest_prediction.get("predictions", [])
            
            optimizations = []
            total_savings = 0.0
            
            for prediction in predictions:
                category_id = prediction["category_id"]
                current_budget = current_budgets.get(category_id, 0)
                predicted_amount = prediction["predicted_amount"]
                
                optimization = self._optimize_category_budget(
                    category_id, current_budget, predicted_amount, rules
                )
                
                if optimization:
                    optimizations.append(optimization)
                    total_savings += optimization.reduction_amount
            
            # Store optimization history
            if user_id not in self.optimization_history:
                self.optimization_history[user_id] = []
            
            optimization_record = {
                "timestamp": datetime.now().isoformat(),
                "optimization_level": optimization_level.value,
                "total_savings": total_savings,
                "optimizations": [self._optimization_to_dict(o) for o in optimizations]
            }
            
            self.optimization_history[user_id].append(optimization_record)
            
            # Publish optimization event
            await publish_event(
                EventType.BUDGET_OPTIMIZATION_APPLIED,
                user_id,
                {
                    "optimization_level": optimization_level.value,
                    "total_savings": total_savings,
                    "categories_optimized": len(optimizations)
                },
                "predictive_budget"
            )
            
            return {
                "status": "success",
                "optimization_level": optimization_level.value,
                "optimizations": [self._optimization_to_dict(o) for o in optimizations],
                "total_savings": total_savings,
                "savings_percentage": (total_savings / sum(current_budgets.values())) * 100 if current_budgets else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize budget: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_optimization_level(self, risk_level: str) -> BudgetOptimizationLevel:
        """Get optimization level based on risk"""
        if risk_level == "critical":
            return BudgetOptimizationLevel.EMERGENCY
        elif risk_level == "high":
            return BudgetOptimizationLevel.AGGRESSIVE
        elif risk_level == "moderate":
            return BudgetOptimizationLevel.MODERATE
        else:
            return BudgetOptimizationLevel.CONSERVATIVE
    
    def _optimize_category_budget(self, category_id: int, current_budget: float, 
                                predicted_amount: float, rules: Dict[str, Any]) -> Optional[BudgetOptimization]:
        """Optimize budget for specific category"""
        try:
            category_name = self._get_category_name(category_id)
            
            # Check if category should be protected
            if category_name.lower() in rules["protected_categories"]:
                return None
            
            # Calculate optimal budget
            if predicted_amount < current_budget:
                # Predicted amount is lower, reduce budget
                reduction_percentage = min(
                    (current_budget - predicted_amount) / current_budget,
                    rules["max_reduction"]
                )
            else:
                # Predicted amount is higher, but still optimize
                reduction_percentage = rules["max_reduction"] * 0.5
            
            reduction_amount = current_budget * reduction_percentage
            optimized_budget = current_budget - reduction_amount
            
            # Determine priority
            if category_name.lower() in rules["priority_categories"]:
                priority = "high"
            elif reduction_percentage > rules["max_reduction"] * 0.7:
                priority = "medium"
            else:
                priority = "low"
            
            # Generate reasoning
            reasoning = self._generate_optimization_reasoning(
                category_name, reduction_percentage, predicted_amount, current_budget
            )
            
            return BudgetOptimization(
                category_id=category_id,
                category_name=category_name,
                current_budget=current_budget,
                optimized_budget=optimized_budget,
                reduction_amount=reduction_amount,
                reduction_percentage=reduction_percentage * 100,
                priority=priority,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Failed to optimize category budget: {e}")
            return None
    
    def _generate_optimization_reasoning(self, category_name: str, reduction_percentage: float,
                                       predicted_amount: float, current_budget: float) -> str:
        """Generate reasoning for budget optimization"""
        try:
            if predicted_amount < current_budget:
                return f"{category_name}: Ennustettu kulutus ({predicted_amount:.0f}€) on alle budjetin ({current_budget:.0f}€). Optimointi säästää {reduction_percentage*100:.1f}%."
            else:
                return f"{category_name}: Kulujen leikkaaminen {reduction_percentage*100:.1f}% auttaa saavuttamaan säästötavoitteet."
        except Exception as e:
            logger.error(f"Failed to generate reasoning: {e}")
            return f"{category_name}: Budjetin optimointi suositeltu."
    
    def _assess_budget_risk(self, predictions: List[BudgetPrediction], total_predicted: float) -> Dict[str, Any]:
        """Assess overall budget risk"""
        try:
            high_risk_categories = [p for p in predictions if p.risk_level == "high"]
            increasing_categories = [p for p in predictions if p.trend_direction == "increasing"]
            
            risk_score = len(high_risk_categories) / len(predictions) if predictions else 0
            trend_score = len(increasing_categories) / len(predictions) if predictions else 0
            
            overall_risk = "low"
            if risk_score > 0.5 or trend_score > 0.7:
                overall_risk = "high"
            elif risk_score > 0.3 or trend_score > 0.5:
                overall_risk = "moderate"
            
            return {
                "overall_risk": overall_risk,
                "risk_score": risk_score,
                "trend_score": trend_score,
                "high_risk_categories": len(high_risk_categories),
                "increasing_categories": len(increasing_categories),
                "total_predicted": total_predicted
            }
            
        except Exception as e:
            logger.error(f"Failed to assess budget risk: {e}")
            return {"overall_risk": "unknown"}
    
    def _prediction_to_dict(self, prediction: BudgetPrediction) -> Dict[str, Any]:
        """Convert prediction to dictionary"""
        return {
            "category_id": prediction.category_id,
            "category_name": prediction.category_name,
            "predicted_amount": prediction.predicted_amount,
            "confidence_score": prediction.confidence_score,
            "trend_direction": prediction.trend_direction,
            "risk_level": prediction.risk_level,
            "optimization_suggestions": prediction.optimization_suggestions
        }
    
    def _optimization_to_dict(self, optimization: BudgetOptimization) -> Dict[str, Any]:
        """Convert optimization to dictionary"""
        return {
            "category_id": optimization.category_id,
            "category_name": optimization.category_name,
            "current_budget": optimization.current_budget,
            "optimized_budget": optimization.optimized_budget,
            "reduction_amount": optimization.reduction_amount,
            "reduction_percentage": optimization.reduction_percentage,
            "priority": optimization.priority,
            "reasoning": optimization.reasoning
        }
    
    def get_prediction_history(self, user_id: int) -> Dict[str, Any]:
        """Get user's prediction history"""
        try:
            history = self.prediction_history.get(user_id, [])
            return {
                "status": "success",
                "history": history,
                "total_predictions": len(history)
            }
        except Exception as e:
            logger.error(f"Failed to get prediction history: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_optimization_history(self, user_id: int) -> Dict[str, Any]:
        """Get user's optimization history"""
        try:
            history = self.optimization_history.get(user_id, [])
            return {
                "status": "success",
                "history": history,
                "total_optimizations": len(history)
            }
        except Exception as e:
            logger.error(f"Failed to get optimization history: {e}")
            return {"status": "error", "message": str(e)}

# Global predictive budget instance
predictive_budget = PredictiveBudget() 