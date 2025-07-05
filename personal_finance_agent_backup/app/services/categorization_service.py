"""
ML-powered categorization service for transaction classification.
Implements a learning system that improves from user corrections.
"""
import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models import Transaction, Category, CategoryCorrection, User
from app.core.config import get_data_path, settings
import logging

logger = logging.getLogger(__name__)


class TransactionCategorizationService:
    """
    ML service for categorizing transactions with continuous learning from user feedback.
    Uses scikit-learn with TF-IDF and Logistic Regression for robust text classification.
    """
    
    def __init__(self):
        self.model_path = os.path.join(get_data_path(), "categorization_model.pkl")
        self.vectorizer_path = os.path.join(get_data_path(), "categorization_vectorizer.pkl")
        self.category_encoder_path = os.path.join(get_data_path(), "category_encoder.pkl")
        
        # ML pipeline components
        self.pipeline = None
        self.category_encoder = {}  # Maps category names to IDs and vice versa
        self.is_trained = False
        
        # Feature engineering parameters
        self.max_features = settings.ml_max_features
        self.min_confidence = settings.ml_min_confidence_threshold
        
        # Load existing model if available
        self._load_model()
    
    def categorize_transaction(
        self, 
        description: str, 
        amount: float, 
        merchant: Optional[str] = None,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Categorize a transaction using the trained ML model.
        
        Args:
            description: Transaction description
            amount: Transaction amount
            merchant: Merchant name (optional)
            user_id: User ID for personalized categorization
            db: Database session for accessing user's historical data
            
        Returns:
            Dict containing:
                - category_id: Predicted category ID
                - category_name: Predicted category name
                - confidence: Confidence score (0-1)
                - all_predictions: List of all categories with scores
        """
        if not self.is_trained:
            logger.warning("Model not trained, returning default category")
            return self._get_default_category()
        
        try:
            # Prepare features
            text_features = self._prepare_text_features(description, merchant)
            
            # Get predictions
            probabilities = self.pipeline.predict_proba([text_features])[0]
            predicted_class = self.pipeline.predict([text_features])[0]
            
            # Get confidence score
            max_confidence = max(probabilities)
            
            # If confidence is too low, apply fallback strategies
            if max_confidence < self.min_confidence:
                fallback_result = self._apply_fallback_categorization(
                    description, amount, merchant, user_id, db
                )
                if fallback_result:
                    return fallback_result
            
            # Map predicted class back to category
            category_id = self.category_encoder['class_to_id'].get(predicted_class)
            category_name = self.category_encoder['class_to_name'].get(predicted_class)
            
            # Prepare all predictions for transparency
            all_predictions = []
            classes = self.pipeline.classes_
            for i, prob in enumerate(probabilities):
                class_name = self.category_encoder['class_to_name'].get(classes[i])
                if class_name:
                    all_predictions.append({
                        "category_name": class_name,
                        "confidence": float(prob)
                    })
            
            # Sort by confidence
            all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            result = {
                "category_id": category_id,
                "category_name": category_name,
                "confidence": float(max_confidence),
                "all_predictions": all_predictions[:5],  # Top 5 predictions
                "method": "ml_model"
            }
            
            logger.info(f"Categorized '{description}' as '{category_name}' with confidence {max_confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            return self._get_default_category()
    
    def train_model(self, db: Session, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Train the categorization model using historical transaction data.
        
        Args:
            db: Database session
            force_retrain: Whether to retrain even if model exists
            
        Returns:
            Training statistics and metrics
        """
        logger.info("Starting model training...")
        
        if self.is_trained and not force_retrain:
            logger.info("Model already trained, skipping training")
            return {"status": "skipped", "reason": "model_already_trained"}
        
        # Collect training data
        training_data = self._collect_training_data(db)
        
        if len(training_data) < settings.ml_min_training_samples:
            logger.warning(f"Insufficient training data: {len(training_data)} samples")
            return {
                "status": "failed", 
                "reason": "insufficient_data",
                "samples": len(training_data)
            }
        
        # Prepare features and labels
        X, y = self._prepare_training_data(training_data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create and train pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',  # Could add Finnish stop words
                ngram_range=(1, 2),
                lowercase=True
            )),
            ('classifier', LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight='balanced'  # Handle imbalanced classes
            ))
        ])
        
        # Train the model
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save model
        self._save_model()
        self.is_trained = True
        
        # Log results
        logger.info(f"Model training completed. Accuracy: {accuracy:.3f}")
        
        return {
            "status": "success",
            "accuracy": float(accuracy),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "categories": len(set(y)),
            "features": self.pipeline.named_steps['tfidf'].get_feature_names_out().shape[0] if hasattr(self.pipeline.named_steps['tfidf'], 'get_feature_names_out') else 0
        }
    
    def learn_from_correction(
        self, 
        transaction_id: int, 
        correct_category_id: int, 
        user_id: int,
        db: Session
    ) -> bool:
        """
        Learn from user correction by storing it and potentially retraining.
        
        Args:
            transaction_id: ID of the corrected transaction
            correct_category_id: The correct category ID
            user_id: ID of the user making the correction
            db: Database session
            
        Returns:
            Success status
        """
        try:
            # Store the correction
            correction = CategoryCorrection(
                transaction_id=transaction_id,
                original_category_id=None,  # Would need to be passed or retrieved
                corrected_category_id=correct_category_id,
                user_id=user_id
            )
            
            db.add(correction)
            db.commit()
            
            logger.info(f"Stored correction for transaction {transaction_id}")
            
            # Check if we should retrain
            if self._should_retrain(db):
                logger.info("Triggering model retraining due to accumulated corrections")
                self.train_model(db, force_retrain=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to learn from correction: {e}")
            db.rollback()
            return False
    
    def get_category_suggestions(
        self, 
        description: str, 
        merchant: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get top-k category suggestions for a transaction.
        Useful for providing user with alternatives.
        """
        result = self.categorize_transaction(description, 0.0, merchant)
        
        if result.get("all_predictions"):
            return result["all_predictions"][:top_k]
        else:
            return [{"category_name": result.get("category_name", "Muut"), "confidence": result.get("confidence", 0.0)}]
    
    def _collect_training_data(self, db: Session) -> List[Dict[str, Any]]:
        """Collect training data from transactions and corrections."""
        # Get categorized transactions
        transactions = db.query(Transaction).filter(
            Transaction.category_id.isnot(None),
            Transaction.description.isnot(None)
        ).all()
        
        training_data = []
        
        for txn in transactions:
            # Use corrected category if available
            corrected_category = db.query(CategoryCorrection).filter(
                CategoryCorrection.transaction_id == txn.id
            ).first()
            
            category_id = corrected_category.corrected_category_id if corrected_category else txn.category_id
            
            # Get category name
            category = db.query(Category).filter(Category.id == category_id).first()
            if category:
                training_data.append({
                    "description": txn.description,
                    "merchant": txn.merchant_name,
                    "amount": float(txn.amount),
                    "category_id": category_id,
                    "category_name": category.name
                })
        
        logger.info(f"Collected {len(training_data)} training samples")
        return training_data
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Prepare features and labels for training."""
        X = []
        y = []
        
        # Build category encoder
        unique_categories = list(set(item["category_name"] for item in training_data))
        self.category_encoder = {
            'name_to_id': {name: i for i, name in enumerate(unique_categories)},
            'id_to_name': {i: name for i, name in enumerate(unique_categories)},
            'class_to_name': {i: name for i, name in enumerate(unique_categories)},
            'class_to_id': {i: training_data[0]["category_id"] for i, name in enumerate(unique_categories)}  # Simplified
        }
        
        for item in training_data:
            # Prepare text features
            text_features = self._prepare_text_features(item["description"], item["merchant"])
            X.append(text_features)
            
            # Map category to class
            category_class = self.category_encoder['name_to_id'][item["category_name"]]
            y.append(category_class)
        
        return X, y
    
    def _prepare_text_features(self, description: str, merchant: Optional[str] = None) -> str:
        """Prepare text features for ML model."""
        features = []
        
        if description:
            features.append(description.lower())
        
        if merchant:
            features.append(merchant.lower())
        
        return " ".join(features)
    
    def _apply_fallback_categorization(
        self, 
        description: str, 
        amount: float, 
        merchant: Optional[str],
        user_id: Optional[int],
        db: Optional[Session]
    ) -> Optional[Dict[str, Any]]:
        """Apply rule-based fallback when ML confidence is low."""
        if not db:
            return None
        
        # Rule-based categorization using category keywords
        categories = db.query(Category).all()
        
        best_match = None
        best_score = 0
        
        text_to_match = f"{description} {merchant or ''}".lower()
        
        for category in categories:
            if category.ml_keywords:
                keywords = [kw.strip().lower() for kw in category.ml_keywords.split(',')]
                
                # Simple keyword matching score
                score = sum(1 for keyword in keywords if keyword in text_to_match)
                
                if score > best_score:
                    best_score = score
                    best_match = category
        
        if best_match and best_score > 0:
            return {
                "category_id": best_match.id,
                "category_name": best_match.name,
                "confidence": min(0.8, best_score * 0.2),  # Convert to confidence
                "all_predictions": [{"category_name": best_match.name, "confidence": best_score * 0.2}],
                "method": "rule_based_fallback"
            }
        
        # If no match, return default expense category
        default_category = db.query(Category).filter(
            Category.name == "Muut",
            Category.type == "expense"
        ).first()
        
        if default_category:
            return {
                "category_id": default_category.id,
                "category_name": default_category.name,
                "confidence": 0.1,
                "all_predictions": [{"category_name": default_category.name, "confidence": 0.1}],
                "method": "default_fallback"
            }
        
        return None
    
    def _get_default_category(self) -> Dict[str, Any]:
        """Return default category when model is not available."""
        return {
            "category_id": None,
            "category_name": "Luokittelematon",
            "confidence": 0.0,
            "all_predictions": [{"category_name": "Luokittelematon", "confidence": 0.0}],
            "method": "default"
        }
    
    def _should_retrain(self, db: Session) -> bool:
        """Determine if model should be retrained based on corrections."""
        # Count corrections since last training
        recent_corrections = db.query(CategoryCorrection).filter(
            CategoryCorrection.created_at > datetime.now() - timedelta(days=7)
        ).count()
        
        # Retrain if we have enough new corrections
        return recent_corrections >= settings.ml_retrain_threshold
    
    def _save_model(self):
        """Save trained model to disk."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.pipeline, f)
            
            with open(self.category_encoder_path, 'wb') as f:
                pickle.dump(self.category_encoder, f)
            
            logger.info("Model saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def _load_model(self):
        """Load trained model from disk."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.category_encoder_path):
                with open(self.model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                
                with open(self.category_encoder_path, 'rb') as f:
                    self.category_encoder = pickle.load(f)
                
                self.is_trained = True
                logger.info("Model loaded successfully")
            else:
                logger.info("No trained model found")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_trained = False
    
    def get_model_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about the model and training data."""
        if not self.is_trained:
            return {"status": "not_trained"}
        
        # Count available training data
        training_count = db.query(Transaction).filter(
            Transaction.category_id.isnot(None),
            Transaction.description.isnot(None)
        ).count()
        
        # Count corrections
        corrections_count = db.query(CategoryCorrection).count()
        
        # Get categories
        categories_count = db.query(Category).count()
        
        return {
            "status": "trained",
            "training_samples": training_count,
            "corrections": corrections_count,
            "categories": categories_count,
            "model_features": len(self.category_encoder.get('name_to_id', {})),
            "last_training": os.path.getmtime(self.model_path) if os.path.exists(self.model_path) else None
        } 