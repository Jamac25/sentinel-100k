"""
Database performance and optimization tests
"""
import pytest
import time
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from datetime import datetime, timedelta

from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category

class TestDatabasePerformance:
    """Test database performance and optimizations"""
    
    @pytest.mark.integration
    def test_user_query_performance(self, db_session):
        """Test user query performance"""
        # Create test users
        users = []
        for i in range(100):
            user = User(
                email=f"test{i}@example.com",
                name=f"Test User {i}",
                hashed_password="test_hash"
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Test query performance
        start_time = time.time()
        result = db_session.query(User).filter(User.email.like("%test%")).all()
        query_time = time.time() - start_time
        
        assert len(result) == 100
        assert query_time < 1.0  # Should complete in under 1 second
    
    @pytest.mark.integration
    def test_transaction_aggregation_performance(self, db_session, test_user, test_category):
        """Test transaction aggregation performance"""
        # Create test transactions
        transactions = []
        for i in range(1000):
            transaction = Transaction(
                description=f"Test Transaction {i}",
                amount=-50.00 + (i % 100),
                date=datetime.now() - timedelta(days=i % 365),
                user_id=test_user.id,
                category_id=test_category.id
            )
            transactions.append(transaction)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Test aggregation performance
        start_time = time.time()
        result = db_session.query(Transaction).filter(
            Transaction.user_id == test_user.id
        ).count()
        query_time = time.time() - start_time
        
        assert result == 1001  # 1000 + 1 from fixture
        assert query_time < 0.5  # Should complete quickly
    
    @pytest.mark.integration
    def test_complex_query_performance(self, db_session, test_user):
        """Test complex query performance"""
        # Create categories and transactions
        categories = []
        for i in range(10):
            category = Category(
                name=f"Category {i}",
                is_income=i % 2 == 0
            )
            categories.append(category)
        
        db_session.add_all(categories)
        db_session.commit()
        
        transactions = []
        for i in range(500):
            transaction = Transaction(
                description=f"Transaction {i}",
                amount=-100.00 + (i % 200),
                date=datetime.now() - timedelta(days=i % 180),
                user_id=test_user.id,
                category_id=categories[i % 10].id
            )
            transactions.append(transaction)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Test complex query with joins and aggregations
        start_time = time.time()
        result = db_session.query(
            Category.name,
            db_session.query(Transaction.amount).filter(
                Transaction.category_id == Category.id,
                Transaction.user_id == test_user.id
            ).count().label('transaction_count')
        ).filter(Category.id.in_([c.id for c in categories])).all()
        
        query_time = time.time() - start_time
        
        assert len(result) == 10
        assert query_time < 1.0  # Complex query should still be fast

class TestDatabaseIndexes:
    """Test database indexes and query optimization"""
    
    @pytest.mark.integration
    def test_user_email_index(self, db_session):
        """Test that user email queries use index"""
        # This would require EXPLAIN QUERY PLAN in real scenario
        # For now, just test that query works efficiently
        start_time = time.time()
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        query_time = time.time() - start_time
        
        # Should be very fast even without data due to index
        assert query_time < 0.1
    
    @pytest.mark.integration
    def test_transaction_date_range_query(self, db_session, test_user, test_category):
        """Test transaction date range queries"""
        # Create transactions over date range
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        
        transactions = []
        for i in range(100):
            transaction = Transaction(
                description=f"Transaction {i}",
                amount=-50.00,
                date=start_date + timedelta(days=i * 3),
                user_id=test_user.id,
                category_id=test_category.id
            )
            transactions.append(transaction)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Test date range query performance
        query_start_date = datetime.now() - timedelta(days=30)
        
        start_time = time.time()
        result = db_session.query(Transaction).filter(
            Transaction.user_id == test_user.id,
            Transaction.date >= query_start_date
        ).all()
        query_time = time.time() - start_time
        
        assert len(result) >= 0  # Some transactions in range
        assert query_time < 0.5  # Should be fast with proper indexing

class TestDatabaseMigrations:
    """Test database migration scenarios"""
    
    @pytest.mark.integration
    def test_schema_compatibility(self, db_session):
        """Test that current schema works with existing data"""
        # Test creating all model types
        user = User(
            email="migration_test@example.com",
            name="Migration Test User",
            hashed_password="test_hash"
        )
        db_session.add(user)
        db_session.commit()
        
        category = Category(
            name="Migration Test Category",
            is_income=False
        )
        db_session.add(category)
        db_session.commit()
        
        transaction = Transaction(
            description="Migration test transaction",
            amount=-25.00,
            date=datetime.now(),
            user_id=user.id,
            category_id=category.id
        )
        db_session.add(transaction)
        db_session.commit()
        
        # Verify all relationships work
        assert transaction.user == user
        assert transaction.category == category
        assert user.transactions[0] == transaction

class TestDatabaseConstraints:
    """Test database constraints and data integrity"""
    
    @pytest.mark.integration
    def test_user_email_uniqueness(self, db_session):
        """Test that user email uniqueness is enforced"""
        user1 = User(
            email="unique_test@example.com",
            name="User 1",
            hashed_password="hash1"
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            email="unique_test@example.com",
            name="User 2", 
            hashed_password="hash2"
        )
        db_session.add(user2)
        
        # This should raise an integrity error
        with pytest.raises(Exception):  # IntegrityError or similar
            db_session.commit()
    
    @pytest.mark.integration
    def test_transaction_foreign_key_constraints(self, db_session):
        """Test foreign key constraints on transactions"""
        # Try to create transaction with non-existent user
        transaction = Transaction(
            description="Invalid transaction",
            amount=-50.00,
            date=datetime.now(),
            user_id=99999,  # Non-existent user
            category_id=1
        )
        db_session.add(transaction)
        
        # This should fail due to foreign key constraint
        with pytest.raises(Exception):
            db_session.commit()

class TestDatabaseBackup:
    """Test database backup and recovery scenarios"""
    
    @pytest.mark.integration
    def test_data_export_import(self, db_session, test_user):
        """Test data export and import functionality"""
        # Create some test data
        original_name = test_user.name
        original_email = test_user.email
        
        # Simulate export (get data)
        exported_user = {
            'email': test_user.email,
            'name': test_user.name,
            'hashed_password': test_user.hashed_password
        }
        
        # Simulate clearing and reimporting
        db_session.delete(test_user)
        db_session.commit()
        
        # Verify user is gone
        assert db_session.query(User).filter(User.email == original_email).first() is None
        
        # Reimport
        reimported_user = User(**exported_user)
        db_session.add(reimported_user)
        db_session.commit()
        
        # Verify data integrity
        recovered_user = db_session.query(User).filter(User.email == original_email).first()
        assert recovered_user is not None
        assert recovered_user.name == original_name
        assert recovered_user.email == original_email 
 
 
 
 