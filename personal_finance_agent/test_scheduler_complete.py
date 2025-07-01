"""
Comprehensive Test Suite for Scheduler Service
Tests all scheduler functionality including job scheduling, execution, and error handling.
"""
import pytest
import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the scheduler service and related modules
from app.services.scheduler_service import (
    SchedulerService, 
    process_pending_documents,
    train_ml_models,
    update_agent_moods,
    cleanup_old_documents,
    cleanup_logs,
    backup_database,
    scheduler_service
)
from app.models import Document, ProcessingStatus, User, Transaction, AgentState
from app.db.base import Base
from app.core.config import settings


@pytest.fixture
def test_db():
    """Create a test database for scheduler tests."""
    # Create temporary SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Mock the SessionLocal in scheduler service
    with patch('app.services.scheduler_service.SessionLocal', TestSessionLocal):
        yield TestSessionLocal


@pytest.fixture
def scheduler():
    """Create a scheduler instance for testing."""
    scheduler = SchedulerService()
    yield scheduler
    # Clean up
    if scheduler.is_running:
        scheduler.stop()


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing."""
    db = test_db()
    user = User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    
    # Create agent state
    agent_state = AgentState(
        user_id=1,
        mood_score=50,
        emotional_state="neutral",
        last_mood_update=datetime.now()
    )
    db.add(agent_state)
    db.commit()
    
    return user


@pytest.fixture
def sample_document(test_db, sample_user):
    """Create a sample document for testing."""
    db = test_db()
    document = Document(
        id=1,
        user_id=sample_user.id,
        filename="test_receipt.pdf",
        file_path="/tmp/test_receipt.pdf",
        file_size=1024,
        mime_type="application/pdf",
        processing_status=ProcessingStatus.PENDING,
        created_at=datetime.now()
    )
    db.add(document)
    db.commit()
    return document


class TestSchedulerService:
    """Test cases for the SchedulerService class."""
    
    def test_scheduler_initialization(self, scheduler):
        """Test scheduler initializes correctly."""
        assert scheduler is not None
        assert scheduler.scheduler is not None
        assert not scheduler.is_running
    
    def test_scheduler_start_stop(self, scheduler):
        """Test scheduler starts and stops correctly."""
        # Test start
        scheduler.start()
        assert scheduler.is_running
        
        # Test stop
        scheduler.stop()
        assert not scheduler.is_running
    
    def test_scheduler_start_when_already_running(self, scheduler, caplog):
        """Test starting scheduler when already running logs warning."""
        scheduler.start()
        
        # Try to start again
        scheduler.start()
        assert "Scheduler already running" in caplog.text
        
        scheduler.stop()
    
    def test_get_scheduler_status_stopped(self, scheduler):
        """Test getting status when scheduler is stopped."""
        status = scheduler.get_scheduler_status()
        assert status["status"] == "stopped"
    
    def test_get_scheduler_status_running(self, scheduler):
        """Test getting status when scheduler is running."""
        scheduler.start()
        status = scheduler.get_scheduler_status()
        
        assert status["status"] == "running"
        assert "jobs" in status
        assert "job_count" in status
        assert isinstance(status["jobs"], list)
        
        scheduler.stop()
    
    def test_trigger_job_success(self, scheduler):
        """Test manually triggering a job."""
        scheduler.start()
        
        # Mock a job
        mock_job = Mock()
        mock_job.id = "test_job"
        
        with patch.object(scheduler.scheduler, 'get_job', return_value=mock_job):
            result = scheduler.trigger_job("test_job")
            assert result is True
            mock_job.modify.assert_called_once()
        
        scheduler.stop()
    
    def test_trigger_job_not_found(self, scheduler):
        """Test triggering a non-existent job."""
        scheduler.start()
        
        with patch.object(scheduler.scheduler, 'get_job', return_value=None):
            result = scheduler.trigger_job("nonexistent_job")
            assert result is False
        
        scheduler.stop()


class TestScheduledTasks:
    """Test cases for scheduled task functions."""
    
    @patch('app.services.scheduler_service.document_service')
    @patch('app.services.scheduler_service.ocr_engine')
    def test_process_pending_documents_success(self, mock_ocr, mock_doc_service, test_db, sample_document):
        """Test successful document processing."""
        # Mock successful OCR result
        mock_ocr.process_document.return_value = {
            "raw_text": "Receipt for 25.50€",
            "confidence": 0.95,
            "service_used": "tesseract",
            "parsed_data": {
                "amount": 25.50,
                "merchant": "Test Store",
                "date": datetime.now()
            }
        }
        
        # Mock document service
        mock_doc_service.get_processing_queue.return_value = [sample_document]
        mock_doc_service.mark_processing_started.return_value = True
        mock_doc_service.mark_processing_completed.return_value = True
        
        # Run the task
        process_pending_documents()
        
        # Verify calls
        mock_doc_service.get_processing_queue.assert_called_once()
        mock_doc_service.mark_processing_started.assert_called_once()
        mock_ocr.process_document.assert_called_once()
        mock_doc_service.mark_processing_completed.assert_called_once()
    
    @patch('app.services.scheduler_service.document_service')
    @patch('app.services.scheduler_service.ocr_engine')
    def test_process_pending_documents_ocr_error(self, mock_ocr, mock_doc_service, test_db, sample_document):
        """Test document processing with OCR error."""
        # Mock OCR error
        mock_ocr.process_document.return_value = {
            "error": "OCR processing failed"
        }
        
        mock_doc_service.get_processing_queue.return_value = [sample_document]
        mock_doc_service.mark_processing_started.return_value = True
        mock_doc_service.mark_processing_failed.return_value = True
        
        # Run the task
        process_pending_documents()
        
        # Verify error handling
        mock_doc_service.mark_processing_failed.assert_called_once()
    
    @patch('app.services.scheduler_service.document_service')
    def test_process_pending_documents_no_documents(self, mock_doc_service, test_db):
        """Test document processing when no documents are pending."""
        mock_doc_service.get_processing_queue.return_value = []
        
        # Run the task - should return early
        process_pending_documents()
        
        # Verify only queue check was made
        mock_doc_service.get_processing_queue.assert_called_once()
        mock_doc_service.mark_processing_started.assert_not_called()
    
    @patch('app.services.scheduler_service.categorization_service')
    def test_train_ml_models_success(self, mock_categorization_service, test_db):
        """Test successful ML model training."""
        mock_categorization_service.train_model.return_value = {
            "status": "success",
            "accuracy": 0.85
        }
        
        # Run the task
        train_ml_models()
        
        # Verify training was called
        mock_categorization_service.train_model.assert_called_once()
    
    @patch('app.services.scheduler_service.categorization_service')
    def test_train_ml_models_failure(self, mock_categorization_service, test_db, caplog):
        """Test ML model training failure."""
        mock_categorization_service.train_model.return_value = {
            "status": "failed",
            "reason": "Insufficient training data"
        }
        
        # Run the task
        train_ml_models()
        
        # Verify warning was logged
        assert "ML training failed" in caplog.text
    
    def test_update_agent_moods(self, test_db, sample_user):
        """Test agent mood update functionality."""
        db = test_db()
        
        # Create some transactions
        income_transaction = Transaction(
            user_id=sample_user.id,
            amount=-1000.0,  # Negative for income
            description="Salary",
            transaction_date=datetime.now() - timedelta(days=5),
            type="income"
        )
        
        expense_transaction = Transaction(
            user_id=sample_user.id,
            amount=200.0,  # Positive for expense
            description="Groceries",
            transaction_date=datetime.now() - timedelta(days=3),
            type="expense"
        )
        
        db.add(income_transaction)
        db.add(expense_transaction)
        db.commit()
        
        # Run the task
        update_agent_moods()
        
        # Verify mood was updated
        db.refresh(sample_user.agent_state)
        assert sample_user.agent_state.mood_score > 50  # Should be positive due to high savings rate
    
    @patch('app.services.scheduler_service.document_service')
    def test_cleanup_old_documents(self, mock_doc_service, test_db):
        """Test cleanup of old documents."""
        # Mock old documents
        mock_doc_service.delete_document.return_value = True
        
        # Run the task
        cleanup_old_documents()
        
        # Verify cleanup attempt (exact verification depends on database state)
        # This test validates the function runs without errors
    
    @patch('glob.glob')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_cleanup_logs(self, mock_remove, mock_getmtime, mock_glob):
        """Test log file cleanup."""
        # Mock old log files
        old_time = datetime.now() - timedelta(days=35)
        mock_glob.return_value = ['/tmp/old.log.1', '/tmp/old.log.2']
        mock_getmtime.return_value = old_time.timestamp()
        
        # Run the task
        cleanup_logs()
        
        # Verify files were removed
        assert mock_remove.call_count == 2
    
    @patch('shutil.copy2')
    @patch('os.makedirs')
    def test_backup_database_sqlite(self, mock_makedirs, mock_copy):
        """Test database backup for SQLite."""
        with patch.object(settings, 'database_url', 'sqlite:///./test.db'):
            # Run the task
            backup_database()
            
            # Verify backup was attempted
            mock_makedirs.assert_called_once()
            mock_copy.assert_called_once()
    
    def test_backup_database_non_sqlite(self, caplog):
        """Test database backup skips non-SQLite databases."""
        with patch.object(settings, 'database_url', 'postgresql://user:pass@localhost/db'):
            # Run the task
            backup_database()
            
            # Verify skip message
            assert "Database backup skipped" in caplog.text


class TestSchedulerIntegration:
    """Integration tests for scheduler functionality."""
    
    def test_scheduler_with_all_jobs(self, scheduler):
        """Test scheduler with all jobs registered."""
        scheduler.start()
        
        # Verify all expected jobs are registered
        jobs = scheduler.scheduler.get_jobs()
        job_ids = [job.id for job in jobs]
        
        expected_jobs = [
            'process_documents',
            'train_ml_models',
            'update_agent_moods',
            'cleanup_documents',
            'cleanup_logs'
        ]
        
        # Check if backup job is enabled
        if settings.enable_backups:
            expected_jobs.append('backup_database')
        
        for expected_job in expected_jobs:
            assert expected_job in job_ids
        
        scheduler.stop()
    
    @patch('app.services.scheduler_service.process_pending_documents')
    def test_manual_job_trigger(self, mock_process_docs, scheduler):
        """Test manually triggering a job."""
        scheduler.start()
        
        # Trigger document processing job
        result = scheduler.trigger_job('process_documents')
        assert result is True
        
        # Wait a brief moment for job to potentially execute
        import time
        time.sleep(0.1)
        
        scheduler.stop()


class TestErrorHandling:
    """Test error handling in scheduler functions."""
    
    @patch('app.services.scheduler_service.SessionLocal')
    def test_process_documents_database_error(self, mock_session):
        """Test process_pending_documents handles database errors."""
        mock_session.side_effect = Exception("Database connection failed")
        
        # Should not raise exception
        process_pending_documents()
    
    @patch('app.services.scheduler_service.SessionLocal')
    def test_train_ml_models_database_error(self, mock_session):
        """Test train_ml_models handles database errors."""
        mock_session.side_effect = Exception("Database connection failed")
        
        # Should not raise exception
        train_ml_models()
    
    @patch('app.services.scheduler_service.SessionLocal')
    def test_update_agent_moods_database_error(self, mock_session):
        """Test update_agent_moods handles database errors."""
        mock_session.side_effect = Exception("Database connection failed")
        
        # Should not raise exception
        update_agent_moods()


def test_scheduler_service_singleton():
    """Test that scheduler_service is properly initialized."""
    assert scheduler_service is not None
    assert isinstance(scheduler_service, SchedulerService)


def test_scheduler_configuration():
    """Test scheduler configuration is correct."""
    scheduler = SchedulerService()
    
    # Test configuration values
    assert scheduler.scheduler is not None
    
    # Verify timezone configuration
    assert scheduler.scheduler.timezone.zone == 'Europe/Helsinki'


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"]) 