"""
Scheduled tasks service for background processing and periodic operations.
Uses APScheduler for reliable task scheduling and document processing queues.
"""
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from sqlalchemy.orm import sessionmaker
from app.db.init_db import SessionLocal
from app.models import Document, ProcessingStatus, User, Transaction, AgentState
from app.services.document_service import DocumentService
from app.services.ocr_service import OCREngine
from app.services.categorization_service import TransactionCategorizationService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

document_service = DocumentService()
ocr_engine = OCREngine()
categorization_service = TransactionCategorizationService()


class SchedulerService:
    """
    Background task scheduler for document processing and periodic maintenance.
    Handles OCR processing, ML model training, and system maintenance tasks.
    """
    
    def __init__(self):
        self.scheduler = None
        self.is_running = False
        
        # Configure scheduler
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """Configure APScheduler with database persistence."""
        jobstores = {
            'default': SQLAlchemyJobStore(url=str(settings.database_url))
        }
        
        executors = {
            'default': ThreadPoolExecutor(max_workers=settings.scheduler_max_workers),
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Europe/Helsinki'  # Finnish timezone
        )
    
    def start(self):
        """Start the scheduler and register all scheduled tasks."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        try:
            self.scheduler.start()
            self.is_running = True
            
            # Register periodic tasks
            self._register_document_processing_task()
            self._register_ml_training_task()
            self._register_agent_mood_update_task()
            self._register_cleanup_tasks()
            self._register_backup_tasks()
            
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler gracefully."""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def _register_document_processing_task(self):
        """Register document processing task to run every minute."""
        self.scheduler.add_job(
            func=process_pending_documents,
            trigger=IntervalTrigger(minutes=1),
            id='process_documents',
            name='Process Pending Documents',
            replace_existing=True
        )
        logger.info("Registered document processing task")
    
    def _register_ml_training_task(self):
        """Register ML model training task to run daily."""
        self.scheduler.add_job(
            func=train_ml_models,
            trigger=CronTrigger(hour=2, minute=0),  # 2:00 AM daily
            id='train_ml_models',
            name='Train ML Models',
            replace_existing=True
        )
        logger.info("Registered ML training task")
    
    def _register_agent_mood_update_task(self):
        """Register agent mood update task."""
        self.scheduler.add_job(
            func=self._update_agent_moods,
            trigger=IntervalTrigger(hours=4),  # Every 4 hours
            id='update_agent_moods',
            name='Update Agent Moods',
            replace_existing=True
        )
        logger.info("Registered agent mood update task")
    
    def _register_cleanup_tasks(self):
        """Register system cleanup tasks."""
        # Clean old processed documents
        self.scheduler.add_job(
            func=self._cleanup_old_documents,
            trigger=CronTrigger(hour=3, minute=0),  # 3:00 AM daily
            id='cleanup_documents',
            name='Cleanup Old Documents',
            replace_existing=True
        )
        
        # Clean old log files
        self.scheduler.add_job(
            func=self._cleanup_logs,
            trigger=CronTrigger(day_of_week='sun', hour=1, minute=0),  # Weekly
            id='cleanup_logs',
            name='Cleanup Log Files',
            replace_existing=True
        )
        
        logger.info("Registered cleanup tasks")
    
    def _register_backup_tasks(self):
        """Register data backup tasks."""
        if settings.enable_backups:
            self.scheduler.add_job(
                func=self._backup_database,
                trigger=CronTrigger(hour=0, minute=30),  # 12:30 AM daily
                id='backup_database',
                name='Backup Database',
                replace_existing=True
            )
            logger.info("Registered backup tasks")
    
    async def _update_agent_moods(self):
        """Update agent mood states based on user financial progress."""
        try:
            with SessionLocal() as db:
                # Get all users with agent states
                users = db.query(User).join(AgentState).all()
                
                for user in users:
                    try:
                        # Calculate financial metrics
                        recent_transactions = db.query(Transaction).filter(
                            Transaction.user_id == user.id,
                            Transaction.transaction_date >= datetime.now() - timedelta(days=30)
                        ).all()
                        
                        # Simple mood calculation based on spending vs savings
                        total_expenses = sum(t.amount for t in recent_transactions if t.amount > 0)
                        total_income = sum(abs(t.amount) for t in recent_transactions if t.amount < 0)
                        
                        # Calculate savings rate
                        savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0
                        
                        # Update mood based on savings rate
                        new_mood = max(0, min(100, 50 + savings_rate * 50))
                        
                        # Update agent state
                        agent_state = user.agent_state
                        if agent_state:
                            old_mood = agent_state.mood_score
                            agent_state.mood_score = new_mood
                            agent_state.last_mood_update = datetime.now()
                            
                            # Update emotional state based on mood change
                            if new_mood > old_mood + 10:
                                agent_state.emotional_state = "excited"
                            elif new_mood < old_mood - 10:
                                agent_state.emotional_state = "concerned"
                            else:
                                agent_state.emotional_state = "neutral"
                            
                            db.commit()
                            
                            logger.info(f"Updated mood for user {user.id}: {old_mood} -> {new_mood}")
                        
                    except Exception as e:
                        logger.error(f"Failed to update mood for user {user.id}: {e}")
                        
        except Exception as e:
            logger.error(f"Agent mood update task failed: {e}")
    
    async def _cleanup_old_documents(self):
        """Clean up old processed documents based on retention policy."""
        try:
            with SessionLocal() as db:
                # Delete documents older than retention period
                cutoff_date = datetime.now() - timedelta(days=settings.document_retention_days)
                
                old_documents = db.query(Document).filter(
                    Document.created_at < cutoff_date,
                    Document.processing_status == ProcessingStatus.COMPLETED
                ).all()
                
                deleted_count = 0
                for doc in old_documents:
                    if document_service.delete_document(doc.id, doc.user_id, db):
                        deleted_count += 1
                
                logger.info(f"Cleaned up {deleted_count} old documents")
                
        except Exception as e:
            logger.error(f"Document cleanup task failed: {e}")
    
    async def _cleanup_logs(self):
        """Clean up old log files."""
        try:
            import glob
            
            log_pattern = os.path.join(settings.log_dir, "*.log.*")
            old_logs = []
            
            for log_file in glob.glob(log_pattern):
                # Get file modification time
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < datetime.now() - timedelta(days=30):
                    old_logs.append(log_file)
            
            # Delete old log files
            for log_file in old_logs:
                try:
                    os.remove(log_file)
                except Exception as e:
                    logger.warning(f"Failed to delete log file {log_file}: {e}")
            
            logger.info(f"Cleaned up {len(old_logs)} old log files")
            
        except Exception as e:
            logger.error(f"Log cleanup task failed: {e}")
    
    async def _backup_database(self):
        """Create database backup."""
        try:
            import subprocess
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.sql"
            backup_path = os.path.join(settings.backup_dir, backup_filename)
            
            # Ensure backup directory exists
            os.makedirs(settings.backup_dir, exist_ok=True)
            
            # Create PostgreSQL dump
            cmd = [
                "pg_dump",
                "-h", settings.database_host,
                "-p", str(settings.database_port),
                "-U", settings.database_user,
                "-d", settings.database_name,
                "-f", backup_path,
                "--no-password"
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.database_password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup created: {backup_filename}")
                
                # Clean up old backups (keep last 7 days)
                self._cleanup_old_backups()
                
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Database backup task failed: {e}")
    
    def _cleanup_old_backups(self):
        """Remove backup files older than 7 days."""
        try:
            import glob
            
            backup_pattern = os.path.join(settings.backup_dir, "backup_*.sql")
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for backup_file in glob.glob(backup_pattern):
                file_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
                if file_time < cutoff_time:
                    try:
                        os.remove(backup_file)
                        logger.info(f"Removed old backup: {os.path.basename(backup_file)}")
                    except Exception as e:
                        logger.warning(f"Failed to remove backup {backup_file}: {e}")
                        
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and job information."""
        if not self.is_running:
            return {"status": "stopped"}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": jobs,
            "job_count": len(jobs)
        }
    
    def trigger_job(self, job_id: str) -> bool:
        """Manually trigger a scheduled job."""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now())
                logger.info(f"Triggered job: {job_id}")
                return True
            else:
                logger.warning(f"Job not found: {job_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to trigger job {job_id}: {e}")
            return False


# Define a standalone function for processing documents

def process_pending_documents():
    """Standalone function to process documents waiting for OCR and categorization."""
    try:
        with SessionLocal() as db:
            # Get pending documents
            pending_docs = document_service.get_processing_queue(db, limit=5)

            if not pending_docs:
                return

            logger.info(f"Processing {len(pending_docs)} pending documents")

            for document in pending_docs:
                try:
                    # Mark as processing
                    document_service.mark_processing_started(document.id, db)

                    # Process with OCR
                    ocr_result = ocr_engine.process_document(document.file_path)

                    if ocr_result.get("error"):
                        # Mark as failed
                        document_service.mark_processing_failed(
                            document.id, db, ocr_result["error"]
                        )
                        continue

                    # Mark OCR as completed
                    document_service.mark_processing_completed(
                        document.id, db,
                        extracted_text=ocr_result["raw_text"],
                        extraction_confidence=ocr_result["confidence"],
                        ocr_service_used=ocr_result["service_used"]
                    )

                    # Create transaction if structured data was extracted
                    if ocr_result.get("parsed_data") and ocr_result["parsed_data"].get("amount"):
                        create_transaction_from_ocr(document, ocr_result, db)

                    logger.info(f"Successfully processed document {document.id}")

                except Exception as e:
                    logger.error(f"Failed to process document {document.id}: {e}")
                    document_service.mark_processing_failed(
                        document.id, db, str(e)
                    )

    except Exception as e:
        logger.error(f"Document processing task failed: {e}")


async def create_transaction_from_ocr(document: Document, ocr_result: Dict, db):
    """Create a transaction from OCR results."""
    try:
        parsed_data = ocr_result["parsed_data"]
        
        # Categorize the transaction
        categorization = categorization_service.categorize_transaction(
            description=parsed_data.get("raw_text", ""),
            amount=parsed_data["amount"],
            merchant=parsed_data.get("merchant"),
            user_id=document.user_id,
            db=db
        )
        
        # Create transaction
        transaction = Transaction(
            amount=parsed_data["amount"],
            description=parsed_data.get("raw_text", "")[:500],  # Limit description length
            merchant_name=parsed_data.get("merchant"),
            transaction_date=parsed_data.get("date") or datetime.now(),
            category_id=categorization.get("category_id"),
            ml_confidence=categorization.get("confidence", 0.0),
            document_id=document.id,
            user_id=document.user_id,
            type="expense" if parsed_data["amount"] > 0 else "income"
        )
        
        db.add(transaction)
        db.commit()
        
        logger.info(f"Created transaction from document {document.id}: {parsed_data['amount']}€")
        
    except Exception as e:
        logger.error(f"Failed to create transaction from OCR: {e}")


# Define a standalone function for training ML models

def train_ml_models():
    """Standalone function to train ML models with the latest data."""
    try:
        with SessionLocal() as db:
            logger.info("Starting scheduled ML model training")
            
            # Train categorization model
            training_result = categorization_service.train_model(db, force_retrain=True)
            
            if training_result["status"] == "success":
                logger.info(f"ML training completed successfully. Accuracy: {training_result['accuracy']:.3f}")
            else:
                logger.warning(f"ML training failed: {training_result.get('reason', 'Unknown')}")
                
    except Exception as e:
        logger.error(f"ML training task failed: {e}")


# Global scheduler instance
scheduler_service = SchedulerService() 