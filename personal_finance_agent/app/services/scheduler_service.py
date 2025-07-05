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
from app.services.event_bus import event_bus, EventType, publish_event
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

document_service = DocumentService()
ocr_engine = OCREngine()
categorization_service = TransactionCategorizationService()

class SchedulerService:
    """
    SchedulerService - Keskitetty ajastuspalvelu Sentinel 100K:lle
    
    Ominaisuudet:
    - Yön aikaiset optimoinnit
    - Reaaliaikainen valvonta
    - Automaattiset korjaukset
    - Älykäs säästöautomaatio
    - Event-driven integraatio
    """
    
    def __init__(self):
        self.scheduler = None
        self.is_running = False
        self.ai_services = {
            'watchdog': None,
            'learning': None,
            'ideas': None,
            'memory': None,
            'budget': None
        }
        
        # Configure scheduler
        self._setup_scheduler()
        
        # Register with event bus
        event_bus.register_service("scheduler", self)
    
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
    
    async def start(self):
        """Start the scheduler and register all scheduled tasks."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        try:
            self.scheduler.start()
            self.is_running = True
            
            # Register periodic tasks
            await self._register_nightly_optimizations()
            await self._register_continuous_monitoring()
            await self._register_ai_learning_tasks()
            await self._register_cleanup_tasks()
            await self._register_backup_tasks()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            logger.info("Scheduler started successfully")
            
            # Publish system event
            await publish_event(
                EventType.SCHEDULER_TASK_COMPLETED,
                None,
                {"status": "started", "tasks_registered": True},
                "scheduler_service"
            )
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler gracefully."""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        event_bus.subscribe(EventType.TRANSACTION_CREATED, self._handle_transaction_created)
        event_bus.subscribe(EventType.BUDGET_EXCEEDED, self._handle_budget_exceeded)
        event_bus.subscribe(EventType.EXPENSE_ANOMALY, self._handle_expense_anomaly)
        logger.info("Scheduler subscribed to events")
    
    async def _handle_transaction_created(self, event):
        """Handle new transaction event"""
        try:
            user_id = event.user_id
            transaction_data = event.data
            
            # Trigger immediate categorization if needed
            if not transaction_data.get('category_id'):
                await self._categorize_transaction(user_id, transaction_data)
            
            # Check for budget violations
            await self._check_budget_status(user_id)
            
        except Exception as e:
            logger.error(f"Error handling transaction created event: {e}")
    
    async def _handle_budget_exceeded(self, event):
        """Handle budget exceeded event"""
        try:
            user_id = event.user_id
            budget_data = event.data
            
            # Generate emergency savings ideas
            await self._generate_emergency_savings_ideas(user_id)
            
            # Notify user
            await self._notify_user(user_id, f"Budjetti ylitetty: {budget_data.get('category', 'tuntematon')}")
            
        except Exception as e:
            logger.error(f"Error handling budget exceeded event: {e}")
    
    async def _handle_expense_anomaly(self, event):
        """Handle expense anomaly event"""
        try:
            user_id = event.user_id
            anomaly_data = event.data
            
            # Freeze category if needed
            if anomaly_data.get('severity') == 'high':
                await self._freeze_category(user_id, anomaly_data.get('category'))
            
        except Exception as e:
            logger.error(f"Error handling expense anomaly event: {e}")
    
    async def _register_nightly_optimizations(self):
        """Register nightly optimization tasks."""
        # 02:00 - Siirrä säästöt automaattisesti
        self.scheduler.add_job(
            func=self._auto_transfer_savings,
            trigger=CronTrigger(hour=2, minute=0),
            id='auto_transfer_savings',
            name='Auto Transfer Savings',
            replace_existing=True
        )
        
        # 03:00 - Etsi ja peruuta käyttämättömät tilaukset
        self.scheduler.add_job(
            func=self._cancel_unused_subscriptions,
            trigger=CronTrigger(hour=3, minute=0),
            id='cancel_subscriptions',
            name='Cancel Unused Subscriptions',
            replace_existing=True
        )
        
        # 04:00 - Neuvottele parempia hintoja
        self.scheduler.add_job(
            func=self._negotiate_better_rates,
            trigger=CronTrigger(hour=4, minute=0),
            id='negotiate_rates',
            name='Negotiate Better Rates',
            replace_existing=True
        )
        
        logger.info("Registered nightly optimization tasks")
    
    async def _register_continuous_monitoring(self):
        """Register continuous monitoring tasks."""
        # Reaaliaikainen valvonta joka 5 minuutti
        self.scheduler.add_job(
            func=self._continuous_monitoring,
            trigger=IntervalTrigger(minutes=5),
            id='continuous_monitoring',
            name='Continuous Monitoring',
            replace_existing=True
        )
        
        logger.info("Registered continuous monitoring")
    
    async def _register_ai_learning_tasks(self):
        """Register AI learning and optimization tasks."""
        # Päivittäinen oppiminen
        self.scheduler.add_job(
            func=self._update_learning_models,
            trigger=CronTrigger(hour=1, minute=0),
            id='update_learning',
            name='Update Learning Models',
            replace_existing=True
        )
        
        # Viikoittainen optimointi
        self.scheduler.add_job(
            func=self._weekly_optimization,
            trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
            id='weekly_optimization',
            name='Weekly Optimization',
            replace_existing=True
        )
        
        logger.info("Registered AI learning tasks")
    
    async def _register_cleanup_tasks(self):
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
    
    async def _register_backup_tasks(self):
        """Register backup tasks."""
        # Daily database backup
        self.scheduler.add_job(
            func=self._backup_database,
            trigger=CronTrigger(hour=5, minute=0),  # 5:00 AM daily
            id='backup_database',
            name='Database Backup',
            replace_existing=True
        )
        
        logger.info("Registered backup tasks")
    
    async def _auto_transfer_savings(self):
        """Automaattinen säästösiirto"""
        try:
            db = SessionLocal()
            users = db.query(User).all()
            
            for user in users:
                try:
                    # Laske kuukausitulot ja -menot
                    monthly_income = self._calculate_monthly_income(user.id, db)
                    monthly_expenses = self._calculate_monthly_expenses(user.id, db)
                    
                    # Säästösiirto 20% nettotuloista
                    net_income = monthly_income - monthly_expenses
                    savings_amount = net_income * 0.2
                    
                    if savings_amount > 0:
                        # Luo säästötransaktio
                        savings_transaction = Transaction(
                            user_id=user.id,
                            amount=-savings_amount,  # Negatiivinen = tulo
                            description="Automaattinen säästösiirto",
                            category_id=self._get_savings_category_id(db),
                            transaction_date=datetime.now()
                        )
                        db.add(savings_transaction)
                        
                        # Publish event
                        await publish_event(
                            EventType.SAVINGS_GOAL_UPDATED,
                            user.id,
                            {"amount": savings_amount, "type": "auto_transfer"},
                            "scheduler_service"
                        )
                        
                        logger.info(f"Auto transfer {savings_amount}€ for user {user.id}")
                
                except Exception as e:
                    logger.error(f"Error in auto transfer for user {user.id}: {e}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Auto transfer failed: {e}")
        finally:
            db.close()
    
    async def _cancel_unused_subscriptions(self):
        """Peruuta käyttämättömät tilaukset"""
        try:
            db = SessionLocal()
            users = db.query(User).all()
            
            for user in users:
                try:
                    unused_subscriptions = self._find_unused_subscriptions(user.id, db)
                    
                    for subscription in unused_subscriptions:
                        result = await self._cancel_subscription(subscription)
                        if result.get('success'):
                            logger.info(f"Cancelled subscription {subscription['name']} for user {user.id}")
                
                except Exception as e:
                    logger.error(f"Error cancelling subscriptions for user {user.id}: {e}")
            
        except Exception as e:
            logger.error(f"Cancel subscriptions failed: {e}")
        finally:
            db.close()
    
    async def _negotiate_better_rates(self):
        """Neuvottele parempia hintoja"""
        try:
            db = SessionLocal()
            users = db.query(User).all()
            
            for user in users:
                try:
                    negotiable_services = self._find_negotiable_services(user.id, db)
                    
                    for service in negotiable_services:
                        result = await self._negotiate_service_rate(service)
                        if result.get('success'):
                            logger.info(f"Negotiated better rate for {service['name']} for user {user.id}")
                
                except Exception as e:
                    logger.error(f"Error negotiating rates for user {user.id}: {e}")
            
        except Exception as e:
            logger.error(f"Rate negotiation failed: {e}")
        finally:
            db.close()
    
    async def _continuous_monitoring(self):
        """Reaaliaikainen valvonta"""
        try:
            db = SessionLocal()
            users = db.query(User).all()
            
            for user in users:
                try:
                    # Tarkista epätavalliset menot
                    unusual_expenses = self._detect_unusual_expenses(user.id, db)
                    
                    for expense in unusual_expenses:
                        await publish_event(
                            EventType.EXPENSE_ANOMALY,
                            user.id,
                            expense,
                            "scheduler_service",
                            priority="high"
                        )
                    
                    # Tarkista budjetin tila
                    budget_status = self._check_budget_status(user.id, db)
                    if budget_status.get('exceeded'):
                        await publish_event(
                            EventType.BUDGET_EXCEEDED,
                            user.id,
                            budget_status,
                            "scheduler_service",
                            priority="high"
                        )
                
                except Exception as e:
                    logger.error(f"Error in continuous monitoring for user {user.id}: {e}")
            
        except Exception as e:
            logger.error(f"Continuous monitoring failed: {e}")
        finally:
            db.close()
    
    async def _update_learning_models(self):
        """Päivitä oppimismallit"""
        try:
            await self._update_spending_pattern_model()
            await self._update_savings_optimization_model()
            logger.info("Learning models updated")
            
        except Exception as e:
            logger.error(f"Learning model update failed: {e}")
    
    async def _weekly_optimization(self):
        """Viikoittainen optimointi"""
        try:
            db = SessionLocal()
            users = db.query(User).all()
            
            for user in users:
                try:
                    # Analysoi viikon kulut
                    weekly_analysis = self._analyze_weekly_spending(user.id, db)
                    
                    # Optimoi budjettikategoriat
                    optimizations = self._optimize_budget_categories(weekly_analysis)
                    
                    # Sovella optimoinnit
                    for optimization in optimizations:
                        await self._apply_budget_optimization(user.id, optimization, db)
                    
                    # Generoi seuraavan viikon ideat
                    await self._generate_next_week_ideas(user.email, weekly_analysis)
                
                except Exception as e:
                    logger.error(f"Error in weekly optimization for user {user.id}: {e}")
            
        except Exception as e:
            logger.error(f"Weekly optimization failed: {e}")
        finally:
            db.close()
    
    async def _cleanup_old_documents(self):
        """Clean old processed documents"""
        try:
            db = SessionLocal()
            
            # Delete documents older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            old_documents = db.query(Document).filter(
                Document.created_at < cutoff_date,
                Document.status == ProcessingStatus.COMPLETED
            ).all()
            
            for doc in old_documents:
                # Delete file if exists
                if doc.file_path and os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
                
                # Delete database record
                db.delete(doc)
            
            db.commit()
            logger.info(f"Cleaned up {len(old_documents)} old documents")
            
        except Exception as e:
            logger.error(f"Document cleanup failed: {e}")
        finally:
            db.close()
    
    async def _cleanup_logs(self):
        """Clean old log files"""
        try:
            log_dir = "logs"
            if os.path.exists(log_dir):
                cutoff_date = datetime.now() - timedelta(days=7)
                
                for filename in os.listdir(log_dir):
                    filepath = os.path.join(log_dir, filename)
                    if os.path.isfile(filepath):
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_time < cutoff_date:
                            os.remove(filepath)
                            logger.info(f"Removed old log file: {filename}")
            
        except Exception as e:
            logger.error(f"Log cleanup failed: {e}")
    
    async def _backup_database(self):
        """Backup database"""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"sentinel_backup_{timestamp}.db")
            
            # For SQLite, just copy the file
            if settings.database_url.startswith("sqlite"):
                import shutil
                db_file = settings.database_url.replace("sqlite:///", "")
                shutil.copy2(db_file, backup_file)
                logger.info(f"Database backed up to {backup_file}")
            
            # Clean old backups (keep last 7)
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
    
    def _cleanup_old_backups(self):
        """Clean old backup files"""
        try:
            backup_dir = "backups"
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if f.startswith("sentinel_backup_")]
                backup_files.sort(reverse=True)
                
                # Keep only last 7 backups
                for old_backup in backup_files[7:]:
                    os.remove(os.path.join(backup_dir, old_backup))
                    logger.info(f"Removed old backup: {old_backup}")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    async def _categorize_transaction(self, user_id: int, transaction_data: Dict):
        """Categorize transaction automatically"""
        try:
            result = categorization_service.categorize_transaction(
                description=transaction_data.get('description', ''),
                amount=transaction_data.get('amount', 0),
                user_id=user_id
            )
            
            if result.get('category_id'):
                # Update transaction with category
                db = SessionLocal()
                transaction = db.query(Transaction).filter(
                    Transaction.id == transaction_data.get('id')
                ).first()
                
                if transaction:
                    transaction.category_id = result['category_id']
                    db.commit()
                    
                    await publish_event(
                        EventType.TRANSACTION_CATEGORIZED,
                        user_id,
                        {"transaction_id": transaction.id, "category_id": result['category_id']},
                        "scheduler_service"
                    )
                
                db.close()
        
        except Exception as e:
            logger.error(f"Transaction categorization failed: {e}")
    
    async def _check_budget_status(self, user_id: int, db=None):
        """Check budget status for user"""
        try:
            if not db:
                db = SessionLocal()
            
            # This would check actual budget status
            # For now, return mock data
            return {
                "exceeded": False,
                "categories": [],
                "total_spent": 0,
                "total_budget": 0
            }
        
        except Exception as e:
            logger.error(f"Budget status check failed: {e}")
            return {"exceeded": False}
        finally:
            if not db:
                db.close()
    
    async def _generate_emergency_savings_ideas(self, user_id: int):
        """Generate emergency savings ideas"""
        try:
            # This would integrate with IdeaEngine
            ideas = [
                "Myy käyttämättömiä tavaroita verkossa",
                "Ota lisätyö viikonloppuisin",
                "Leikkaa tilauksia ja kuluja",
                "Käytä julkisia kulkuneuvoja"
            ]
            
            await publish_event(
                EventType.IDEA_GENERATED,
                user_id,
                {"ideas": ideas, "type": "emergency_savings"},
                "scheduler_service"
            )
        
        except Exception as e:
            logger.error(f"Emergency ideas generation failed: {e}")
    
    async def _notify_user(self, user_id: int, message: str):
        """Notify user"""
        try:
            # This would integrate with notification service
            logger.info(f"Notification for user {user_id}: {message}")
            
        except Exception as e:
            logger.error(f"User notification failed: {e}")
    
    async def _freeze_category(self, user_id: int, category: str, db=None):
        """Freeze spending category"""
        try:
            if not db:
                db = SessionLocal()
            
            # This would implement category freezing
            logger.info(f"Freezing category {category} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Category freezing failed: {e}")
        finally:
            if not db:
                db.close()
    
    def _calculate_monthly_income(self, user_id: int, db) -> float:
        """Calculate monthly income for user"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount < 0  # Income is negative
            ).all()
            
            return abs(sum(t.amount for t in transactions))
        
        except Exception as e:
            logger.error(f"Monthly income calculation failed: {e}")
            return 0.0
    
    def _calculate_monthly_expenses(self, user_id: int, db) -> float:
        """Calculate monthly expenses for user"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0  # Expenses are positive
            ).all()
            
            return sum(t.amount for t in transactions)
        
        except Exception as e:
            logger.error(f"Monthly expenses calculation failed: {e}")
            return 0.0
    
    def _find_unused_subscriptions(self, user_id: int, db) -> List[Dict]:
        """Find unused subscriptions"""
        try:
            # This would analyze transaction patterns
            # For now, return mock data
            return [
                {"name": "Netflix", "amount": 15.99, "last_used": "2024-01-01"},
                {"name": "Spotify", "amount": 9.99, "last_used": "2024-01-05"}
            ]
        
        except Exception as e:
            logger.error(f"Unused subscriptions detection failed: {e}")
            return []
    
    async def _cancel_subscription(self, subscription: Dict) -> Dict:
        """Cancel subscription"""
        try:
            # This would integrate with payment providers
            logger.info(f"Cancelling subscription: {subscription['name']}")
            return {"success": True, "subscription": subscription['name']}
        
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _find_negotiable_services(self, user_id: int, db) -> List[Dict]:
        """Find negotiable services"""
        try:
            # This would analyze service providers
            return [
                {"name": "Internet", "current_rate": 29.99, "provider": "DNA"},
                {"name": "Mobile", "current_rate": 19.99, "provider": "Elisa"}
            ]
        
        except Exception as e:
            logger.error(f"Negotiable services detection failed: {e}")
            return []
    
    async def _negotiate_service_rate(self, service: Dict) -> Dict:
        """Negotiate service rate"""
        try:
            # This would integrate with service providers
            logger.info(f"Negotiating rate for {service['name']}")
            return {"success": True, "new_rate": service['current_rate'] * 0.9}
        
        except Exception as e:
            logger.error(f"Rate negotiation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _detect_unusual_expenses(self, user_id: int, db) -> List[Dict]:
        """Detect unusual expenses"""
        try:
            # This would implement anomaly detection
            return [
                {"category": "Viihde", "amount": 500, "severity": "high", "reason": "Unusual spending pattern"}
            ]
        
        except Exception as e:
            logger.error(f"Unusual expenses detection failed: {e}")
            return []
    
    async def _update_spending_pattern_model(self):
        """Update spending pattern model"""
        try:
            # This would retrain ML models
            logger.info("Updating spending pattern model")
        
        except Exception as e:
            logger.error(f"Spending pattern model update failed: {e}")
    
    async def _update_savings_optimization_model(self):
        """Update savings optimization model"""
        try:
            # This would retrain optimization models
            logger.info("Updating savings optimization model")
        
        except Exception as e:
            logger.error(f"Savings optimization model update failed: {e}")
    
    def _analyze_weekly_spending(self, user_id: int, db) -> Dict:
        """Analyze weekly spending"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date
            ).all()
            
            return {
                "total_spent": sum(t.amount for t in transactions if t.amount > 0),
                "total_income": abs(sum(t.amount for t in transactions if t.amount < 0)),
                "transaction_count": len(transactions),
                "categories": {}
            }
        
        except Exception as e:
            logger.error(f"Weekly spending analysis failed: {e}")
            return {}
    
    def _optimize_budget_categories(self, weekly_analysis: Dict) -> List[Dict]:
        """Optimize budget categories"""
        try:
            # This would implement budget optimization logic
            return [
                {"category": "Viihde", "adjustment": -50, "reason": "High spending detected"}
            ]
        
        except Exception as e:
            logger.error(f"Budget optimization failed: {e}")
            return []
    
    async def _apply_budget_optimization(self, user_id: int, optimization: Dict, db):
        """Apply budget optimization"""
        try:
            # This would update budget settings
            logger.info(f"Applying budget optimization for user {user_id}: {optimization}")
        
        except Exception as e:
            logger.error(f"Budget optimization application failed: {e}")
    
    async def _generate_next_week_ideas(self, user_email: str, weekly_analysis: Dict):
        """Generate next week ideas"""
        try:
            # This would integrate with IdeaEngine
            ideas = [
                "Säästä 50€ tällä viikolla",
                "Etsi lisätöitä",
                "Optimoi kulut"
            ]
            
            logger.info(f"Generated ideas for {user_email}: {ideas}")
        
        except Exception as e:
            logger.error(f"Idea generation failed: {e}")
    
    def _get_savings_category_id(self, db) -> int:
        """Get savings category ID"""
        try:
            category = db.query(Category).filter(Category.name == "Säästöt").first()
            return category.id if category else 1
        except Exception as e:
            logger.error(f"Failed to get savings category: {e}")
            return 1
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "jobs": len(self.scheduler.get_jobs()) if self.scheduler else 0,
            "next_run": self.scheduler.get_jobs()[0].next_run_time.isoformat() if self.scheduler and self.scheduler.get_jobs() else None
        }
    
    def trigger_job(self, job_id: str) -> bool:
        """Trigger a specific job"""
        try:
            if self.scheduler:
                self.scheduler.get_job(job_id).modify(next_run_time=datetime.now())
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to trigger job {job_id}: {e}")
            return False

# Global scheduler service instance
scheduler_service = SchedulerService()

# Legacy functions for backward compatibility
def process_pending_documents():
    """Process pending documents (legacy function)"""
    try:
        db = SessionLocal()
        pending_docs = db.query(Document).filter(
            Document.status == ProcessingStatus.PENDING
        ).all()
        
        for doc in pending_docs:
            try:
                # Process document with OCR
                text, confidence = ocr_engine.extract_text(doc.file_path)
                
                # Update document status
                doc.status = ProcessingStatus.COMPLETED
                doc.processed_text = text
                doc.confidence_score = confidence
                
                # Create transaction from OCR result
                asyncio.create_task(create_transaction_from_ocr(doc, {
                    "text": text,
                    "confidence": confidence
                }, db))
                
                logger.info(f"Processed document {doc.id}")
                
            except Exception as e:
                logger.error(f"Failed to process document {doc.id}: {e}")
                doc.status = ProcessingStatus.FAILED
                doc.error_message = str(e)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
    finally:
        db.close()

async def create_transaction_from_ocr(document: Document, ocr_result: Dict, db):
    """Create transaction from OCR result"""
    try:
        # Extract transaction data from OCR text
        text = ocr_result.get("text", "")
        
        # Simple parsing (in real implementation, use more sophisticated parsing)
        lines = text.split('\n')
        amount = 0.0
        description = ""
        
        for line in lines:
            if '€' in line or 'EUR' in line:
                # Extract amount
                import re
                amount_match = re.search(r'(\d+[.,]\d{2})', line)
                if amount_match:
                    amount = float(amount_match.group(1).replace(',', '.'))
            
            if len(line.strip()) > 5 and not amount:
                description = line.strip()
        
        if amount > 0:
            # Create transaction
            transaction = Transaction(
                user_id=document.user_id,
                amount=amount,
                description=description or "OCR extracted transaction",
                transaction_date=document.created_at,
                category_id=1  # Default category
            )
            
            db.add(transaction)
            db.commit()
            
            # Publish event
            await publish_event(
                EventType.TRANSACTION_CREATED,
                document.user_id,
                {"transaction_id": transaction.id, "amount": amount, "description": description},
                "document_service"
            )
            
            logger.info(f"Created transaction from OCR: {amount}€ - {description}")
    
    except Exception as e:
        logger.error(f"Failed to create transaction from OCR: {e}")

def train_ml_models():
    """Train ML models (legacy function)"""
    try:
        db = SessionLocal()
        categorization_service.train_model(db, force_retrain=True)
        logger.info("ML models trained successfully")
    except Exception as e:
        logger.error(f"ML model training failed: {e}")
    finally:
        db.close() 