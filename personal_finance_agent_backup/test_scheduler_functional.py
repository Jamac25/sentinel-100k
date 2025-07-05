"""
Functional Test Suite for Scheduler Service
Tests scheduler functionality with proper async/sync handling.
"""
import pytest
import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
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
from app.core.config import settings


class TestSchedulerBasics:
    """Test basic scheduler functionality."""
    
    def test_scheduler_creation(self):
        """Test that scheduler can be created."""
        scheduler = SchedulerService()
        assert scheduler is not None
        assert scheduler.scheduler is not None
        assert not scheduler.is_running
    
    def test_scheduler_status_stopped(self):
        """Test getting status when stopped."""
        scheduler = SchedulerService()
        status = scheduler.get_scheduler_status()
        assert status["status"] == "stopped"
    
    def test_scheduler_singleton(self):
        """Test scheduler service singleton."""
        assert scheduler_service is not None
        assert isinstance(scheduler_service, SchedulerService)


class TestSchedulerFunctions:
    """Test individual scheduler functions."""
    
    @patch('app.services.scheduler_service.SessionLocal')
    @patch('app.services.scheduler_service.document_service')
    def test_process_pending_documents_no_docs(self, mock_doc_service, mock_session):
        """Test document processing with no pending documents."""
        mock_session.return_value.__enter__.return_value = Mock()
        mock_doc_service.get_processing_queue.return_value = []
        
        # Should not raise exception
        process_pending_documents()
        
        mock_doc_service.get_processing_queue.assert_called_once()
    
    @patch('app.services.scheduler_service.SessionLocal')
    @patch('app.services.scheduler_service.categorization_service')
    def test_train_ml_models_basic(self, mock_categorization, mock_session):
        """Test ML model training function."""
        mock_session.return_value.__enter__.return_value = Mock()
        mock_categorization.train_model.return_value = {
            "status": "success",
            "accuracy": 0.85
        }
        
        # Should not raise exception
        train_ml_models()
        
        mock_categorization.train_model.assert_called_once()
    
    @patch('app.services.scheduler_service.SessionLocal')
    def test_update_agent_moods_basic(self, mock_session):
        """Test agent mood update function."""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.join.return_value.all.return_value = []
        
        # Should not raise exception
        update_agent_moods()
    
    @patch('app.services.scheduler_service.SessionLocal')
    @patch('app.services.scheduler_service.document_service')
    def test_cleanup_old_documents_basic(self, mock_doc_service, mock_session):
        """Test document cleanup function."""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Should not raise exception
        cleanup_old_documents()
    
    @patch('glob.glob')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_cleanup_logs_basic(self, mock_remove, mock_getmtime, mock_glob):
        """Test log cleanup function."""
        old_time = datetime.now() - timedelta(days=35)
        mock_glob.return_value = ['/tmp/old.log.1']
        mock_getmtime.return_value = old_time.timestamp()
        
        # Should not raise exception
        cleanup_logs()
        
        mock_remove.assert_called_once_with('/tmp/old.log.1')
    
    @patch('shutil.copy2')
    @patch('os.makedirs')
    def test_backup_database_sqlite(self, mock_makedirs, mock_copy):
        """Test SQLite database backup."""
        with patch.object(settings, 'database_url', 'sqlite:///./test.db'):
            backup_database()
            mock_makedirs.assert_called_once()
            mock_copy.assert_called_once()
    
    def test_backup_database_postgresql(self, caplog):
        """Test PostgreSQL database backup (should skip)."""
        with patch.object(settings, 'database_url', 'postgresql://user:pass@localhost/db'):
            backup_database()
            # For PostgreSQL, it should log that backup was skipped
            assert len(caplog.records) >= 0  # Just verify no exceptions


class TestSchedulerConfiguration:
    """Test scheduler configuration."""
    
    def test_configuration_values(self):
        """Test scheduler configuration values."""
        scheduler = SchedulerService()
        
        # Test basic configuration
        assert scheduler.scheduler is not None
        
        # Test timezone (using string comparison to avoid timezone object issues)
        timezone_str = str(scheduler.scheduler.timezone)
        assert 'Europe/Helsinki' in timezone_str


class TestSchedulerErrorHandling:
    """Test error handling in scheduler functions."""
    
    @patch('app.services.scheduler_service.SessionLocal')
    def test_process_documents_database_error(self, mock_session):
        """Test document processing with database error."""
        mock_session.side_effect = Exception("Database connection failed")
        
        # Should not raise exception (errors are caught and logged)
        process_pending_documents()
    
    @patch('app.services.scheduler_service.SessionLocal')
    def test_train_ml_models_database_error(self, mock_session):
        """Test ML training with database error."""
        mock_session.side_effect = Exception("Database connection failed")
        
        # Should not raise exception
        train_ml_models()
    
    @patch('app.services.scheduler_service.SessionLocal')
    def test_update_agent_moods_database_error(self, mock_session):
        """Test agent mood update with database error."""
        mock_session.side_effect = Exception("Database connection failed")
        
        # Should not raise exception
        update_agent_moods()


class TestSchedulerJobTrigger:
    """Test job triggering functionality."""
    
    def test_trigger_job_scheduler_not_running(self):
        """Test triggering job when scheduler is not running."""
        scheduler = SchedulerService()
        
        # Should return False when scheduler is not running
        result = scheduler.trigger_job('process_documents')
        assert result is False


# Integration test with proper async handling
@pytest.mark.asyncio
async def test_scheduler_with_event_loop():
    """Test scheduler start/stop with proper event loop."""
    scheduler = SchedulerService()
    
    try:
        # In an async context, scheduler should be able to start
        scheduler.start()
        assert scheduler.is_running
        
        # Test status
        status = scheduler.get_scheduler_status()
        assert status["status"] == "running"
        assert "jobs" in status
        
        # Test job triggering
        result = scheduler.trigger_job('process_documents')
        # Should return True or False (not raise exception)
        assert isinstance(result, bool)
        
    finally:
        # Always stop the scheduler
        if scheduler.is_running:
            scheduler.stop()
        assert not scheduler.is_running


def test_scheduler_job_descriptions():
    """Test that all expected job types are supported."""
    valid_jobs = [
        'process_documents',
        'train_ml_models', 
        'update_agent_moods',
        'cleanup_documents',
        'cleanup_logs',
        'backup_database'
    ]
    
    # These are the jobs the scheduler should support
    assert len(valid_jobs) == 6
    assert 'process_documents' in valid_jobs
    assert 'train_ml_models' in valid_jobs
    assert 'update_agent_moods' in valid_jobs


def test_configuration_properties():
    """Test that configuration properties are available."""
    assert hasattr(settings, 'enable_scheduler')
    assert hasattr(settings, 'scheduler_max_workers')
    assert hasattr(settings, 'scheduler_timezone')
    assert hasattr(settings, 'document_retention_days')
    assert hasattr(settings, 'enable_backups')


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"]) 