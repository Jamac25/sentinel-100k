"""
Sentinel Financial Shield™ - Critical Expense Protection and Emergency Fund Building
Integrates with Watchdog and LiabilitiesInsight for financial protection
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.category import Category
from ..services.event_bus import EventType, publish_event
import logging
import json
import asyncio
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ShieldLevel(Enum):
    """Financial shield protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    EMERGENCY = "emergency"

class ProtectionType(Enum):
    """Types of financial protection"""
    CRITICAL_EXPENSES = "critical_expenses"
    EMERGENCY_FUND = "emergency_fund"
    DEBT_PROTECTION = "debt_protection"
    INCOME_PROTECTION = "income_protection"
    INSURANCE_OPTIMIZATION = "insurance_optimization"

@dataclass
class ShieldProtection:
    """Financial protection configuration"""
    protection_type: ProtectionType
    is_active: bool
    target_amount: float
    current_amount: float
    monthly_contribution: float
    priority: str  # high, medium, low
    description: str
    last_updated: datetime

@dataclass
class EmergencyFund:
    """Emergency fund data structure"""
    target_months: int
    monthly_expenses: float
    target_amount: float
    current_amount: float
    contribution_rate: float
    completion_percentage: float
    estimated_completion_date: datetime

class FinancialShield:
    """
    Sentinel Financial Shield™ - Financial Protection System
    
    Features:
    - Critical expense protection with automatic transfers
    - Emergency fund building with smart contributions
    - Debt cycle prevention and warnings
    - Consumption credit monitoring and limits
    - Insurance optimization and coverage tracking
    """
    
    def __init__(self):
        self.user_protections = {}  # user_id -> Dict[ProtectionType, ShieldProtection]
        self.emergency_funds = {}  # user_id -> EmergencyFund
        self.protection_history = {}  # user_id -> List[Dict]
        self.shield_alerts = {}  # user_id -> List[Dict]
        
        # Protection configurations
        self.protection_configs = {
            ProtectionType.CRITICAL_EXPENSES: {
                "priority": "high",
                "description": "Suojaa kriittiset kulut (vuokra, sähkö, ruoka)",
                "target_percentage": 0.15,  # 15% of income
                "auto_transfer": True
            },
            ProtectionType.EMERGENCY_FUND: {
                "priority": "high",
                "description": "Hätävaran rakentaminen 3-6 kuukauden kuluille",
                "target_months": 6,
                "contribution_rate": 0.10  # 10% of income
            },
            ProtectionType.DEBT_PROTECTION: {
                "priority": "medium",
                "description": "Velkakierteen ennaltaehkäisy ja varoitukset",
                "monitoring_enabled": True,
                "alert_threshold": 0.4  # 40% debt-to-income ratio
            },
            ProtectionType.INCOME_PROTECTION: {
                "priority": "medium",
                "description": "Tulojen suojaaminen ja sivutulojen kehittäminen",
                "diversification_target": 3,  # 3 income sources
                "backup_plan": True
            },
            ProtectionType.INSURANCE_OPTIMIZATION: {
                "priority": "low",
                "description": "Vakuutusten optimointi ja kattavuuden seuranta",
                "review_frequency": "quarterly",
                "coverage_analysis": True
            }
        }
        
        # Critical expense categories
        self.critical_categories = [
            "Housing", "Utilities", "Food", "Transportation", "Healthcare", "Insurance"
        ]
        
        # Debt categories to monitor
        self.debt_categories = [
            "Credit Cards", "Personal Loans", "Car Loans", "Student Loans", "Payday Loans"
        ]
    
    async def activate_protection(self, user_id: int, protection_type: ProtectionType, 
                                db: Session) -> Dict[str, Any]:
        """Activate financial protection for user"""
        try:
            # Get user's financial status
            user_status = await self._analyze_user_financial_status(user_id, db)
            
            # Create protection configuration
            protection = await self._create_protection_config(user_id, protection_type, user_status)
            
            # Store protection
            if user_id not in self.user_protections:
                self.user_protections[user_id] = {}
            
            self.user_protections[user_id][protection_type] = protection
            
            # Initialize emergency fund if needed
            if protection_type == ProtectionType.EMERGENCY_FUND:
                await self._initialize_emergency_fund(user_id, user_status)
            
            # Publish protection activation event
            await publish_event(
                EventType.SHIELD_ACTIVATED,
                user_id,
                {
                    "protection_type": protection_type.value,
                    "target_amount": protection.target_amount,
                    "monthly_contribution": protection.monthly_contribution
                },
                "financial_shield"
            )
            
            return {
                "status": "success",
                "protection": self._protection_to_dict(protection),
                "activation_message": self._generate_activation_message(protection_type),
                "next_steps": self._generate_next_steps(protection_type)
            }
            
        except Exception as e:
            logger.error(f"Failed to activate protection: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _analyze_user_financial_status(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Analyze user's current financial status"""
        try:
            # Get user's income and expenses
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date
            ).all()
            
            # Calculate income and expenses
            income = sum(abs(t.amount) for t in transactions if t.amount < 0)
            expenses = sum(t.amount for t in transactions if t.amount > 0)
            
            # Calculate monthly averages
            monthly_income = income / 3
            monthly_expenses = expenses / 3
            
            # Analyze critical expenses
            critical_expenses = self._analyze_critical_expenses(transactions)
            
            # Analyze debt situation
            debt_analysis = self._analyze_debt_situation(transactions)
            
            return {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "savings_rate": (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0,
                "critical_expenses": critical_expenses,
                "debt_analysis": debt_analysis,
                "risk_level": self._determine_risk_level(monthly_income, monthly_expenses, debt_analysis)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze financial status: {e}")
            return {}
    
    def _analyze_critical_expenses(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Analyze critical expenses"""
        try:
            critical_total = 0
            critical_breakdown = {}
            
            for transaction in transactions:
                if transaction.amount > 0:  # Expenses
                    category_name = self._get_category_name(transaction.category_id)
                    if any(critical in category_name.lower() for critical in 
                          ["housing", "utilities", "food", "transportation", "healthcare"]):
                        critical_total += transaction.amount
                        critical_breakdown[category_name] = critical_breakdown.get(category_name, 0) + transaction.amount
            
            return {
                "total": critical_total,
                "breakdown": critical_breakdown,
                "percentage_of_expenses": critical_total / sum(t.amount for t in transactions if t.amount > 0) if transactions else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze critical expenses: {e}")
            return {"total": 0, "breakdown": {}, "percentage_of_expenses": 0}
    
    def _analyze_debt_situation(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Analyze debt situation"""
        try:
            debt_payments = 0
            debt_categories = {}
            
            for transaction in transactions:
                if transaction.amount > 0:  # Payments
                    category_name = self._get_category_name(transaction.category_id)
                    if any(debt in category_name.lower() for debt in 
                          ["credit", "loan", "debt", "interest"]):
                        debt_payments += transaction.amount
                        debt_categories[category_name] = debt_categories.get(category_name, 0) + transaction.amount
            
            return {
                "total_payments": debt_payments,
                "categories": debt_categories,
                "debt_to_income_ratio": debt_payments / sum(abs(t.amount) for t in transactions if t.amount < 0) if transactions else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze debt situation: {e}")
            return {"total_payments": 0, "categories": {}, "debt_to_income_ratio": 0}
    
    def _determine_risk_level(self, monthly_income: float, monthly_expenses: float, 
                            debt_analysis: Dict[str, Any]) -> str:
        """Determine financial risk level"""
        try:
            if monthly_income == 0:
                return "critical"
            
            # Calculate risk factors
            savings_rate = (monthly_income - monthly_expenses) / monthly_income
            debt_ratio = debt_analysis.get("debt_to_income_ratio", 0)
            
            if savings_rate < 0 or debt_ratio > 0.5:
                return "critical"
            elif savings_rate < 0.1 or debt_ratio > 0.3:
                return "high"
            elif savings_rate < 0.2 or debt_ratio > 0.2:
                return "moderate"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Failed to determine risk level: {e}")
            return "moderate"
    
    async def _create_protection_config(self, user_id: int, protection_type: ProtectionType, 
                                      user_status: Dict[str, Any]) -> ShieldProtection:
        """Create protection configuration"""
        try:
            config = self.protection_configs[protection_type]
            monthly_income = user_status.get("monthly_income", 3000)
            
            if protection_type == ProtectionType.CRITICAL_EXPENSES:
                target_amount = monthly_income * config["target_percentage"]
                monthly_contribution = target_amount * 0.1  # 10% of target
            elif protection_type == ProtectionType.EMERGENCY_FUND:
                monthly_expenses = user_status.get("monthly_expenses", 2000)
                target_amount = monthly_expenses * config["target_months"]
                monthly_contribution = monthly_income * config["contribution_rate"]
            else:
                target_amount = monthly_income * 0.1  # Default 10% of income
                monthly_contribution = monthly_income * 0.05  # Default 5% of income
            
            return ShieldProtection(
                protection_type=protection_type,
                is_active=True,
                target_amount=target_amount,
                current_amount=0,  # Will be updated based on actual savings
                monthly_contribution=monthly_contribution,
                priority=config["priority"],
                description=config["description"],
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to create protection config: {e}")
            raise
    
    async def _initialize_emergency_fund(self, user_id: int, user_status: Dict[str, Any]):
        """Initialize emergency fund for user"""
        try:
            monthly_expenses = user_status.get("monthly_expenses", 2000)
            monthly_income = user_status.get("monthly_income", 3000)
            
            emergency_fund = EmergencyFund(
                target_months=6,
                monthly_expenses=monthly_expenses,
                target_amount=monthly_expenses * 6,
                current_amount=0,
                contribution_rate=0.1,  # 10% of income
                completion_percentage=0,
                estimated_completion_date=datetime.now() + timedelta(days=365)  # 1 year estimate
            )
            
            self.emergency_funds[user_id] = emergency_fund
            
        except Exception as e:
            logger.error(f"Failed to initialize emergency fund: {e}")
    
    async def update_protection_status(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Update protection status and progress"""
        try:
            if user_id not in self.user_protections:
                return {"status": "error", "message": "No active protections found"}
            
            # Get current financial status
            user_status = await self._analyze_user_financial_status(user_id, db)
            
            # Update each protection
            updated_protections = []
            for protection_type, protection in self.user_protections[user_id].items():
                updated_protection = await self._update_protection_progress(
                    user_id, protection, user_status
                )
                updated_protections.append(updated_protection)
                
                # Check for alerts
                alerts = await self._check_protection_alerts(user_id, updated_protection, user_status)
                if alerts:
                    await self._publish_alerts(user_id, alerts)
            
            # Update emergency fund
            if user_id in self.emergency_funds:
                await self._update_emergency_fund(user_id, user_status)
            
            return {
                "status": "success",
                "protections": [self._protection_to_dict(p) for p in updated_protections],
                "emergency_fund": self._emergency_fund_to_dict(self.emergency_funds.get(user_id)),
                "risk_level": user_status.get("risk_level", "moderate")
            }
            
        except Exception as e:
            logger.error(f"Failed to update protection status: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _update_protection_progress(self, user_id: int, protection: ShieldProtection, 
                                        user_status: Dict[str, Any]) -> ShieldProtection:
        """Update protection progress"""
        try:
            # Calculate current amount based on protection type
            if protection.protection_type == ProtectionType.CRITICAL_EXPENSES:
                current_amount = user_status.get("critical_expenses", {}).get("total", 0)
            elif protection.protection_type == ProtectionType.EMERGENCY_FUND:
                current_amount = self.emergency_funds.get(user_id, EmergencyFund(0, 0, 0, 0, 0, 0, datetime.now())).current_amount
            else:
                # Estimate based on savings rate
                savings_rate = user_status.get("savings_rate", 0)
                monthly_income = user_status.get("monthly_income", 3000)
                current_amount = monthly_income * savings_rate * 3  # 3 months of savings
            
            protection.current_amount = current_amount
            protection.last_updated = datetime.now()
            
            return protection
            
        except Exception as e:
            logger.error(f"Failed to update protection progress: {e}")
            return protection
    
    async def _update_emergency_fund(self, user_id: int, user_status: Dict[str, Any]):
        """Update emergency fund progress"""
        try:
            if user_id not in self.emergency_funds:
                return
            
            emergency_fund = self.emergency_funds[user_id]
            
            # Calculate current amount based on savings
            savings_rate = user_status.get("savings_rate", 0)
            monthly_income = user_status.get("monthly_income", 3000)
            monthly_savings = monthly_income * savings_rate
            
            # Estimate current emergency fund (assuming 3 months of savings)
            emergency_fund.current_amount = monthly_savings * 3
            
            # Calculate completion percentage
            emergency_fund.completion_percentage = min(100, (emergency_fund.current_amount / emergency_fund.target_amount) * 100)
            
            # Estimate completion date
            if monthly_savings > 0:
                remaining_amount = emergency_fund.target_amount - emergency_fund.current_amount
                months_to_complete = remaining_amount / monthly_savings
                emergency_fund.estimated_completion_date = datetime.now() + timedelta(days=months_to_complete * 30)
            
        except Exception as e:
            logger.error(f"Failed to update emergency fund: {e}")
    
    async def _check_protection_alerts(self, user_id: int, protection: ShieldProtection, 
                                     user_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for protection alerts"""
        try:
            alerts = []
            
            # Check critical expense protection
            if protection.protection_type == ProtectionType.CRITICAL_EXPENSES:
                critical_expenses = user_status.get("critical_expenses", {})
                if critical_expenses.get("percentage_of_expenses", 0) > 0.8:
                    alerts.append({
                        "type": "critical_expenses_high",
                        "message": "Kriittiset kulut ovat korkealla tasolla",
                        "priority": "high",
                        "action_required": "Harkitse kulujen leikkaamista"
                    })
            
            # Check debt protection
            if protection.protection_type == ProtectionType.DEBT_PROTECTION:
                debt_ratio = user_status.get("debt_analysis", {}).get("debt_to_income_ratio", 0)
                if debt_ratio > 0.4:
                    alerts.append({
                        "type": "debt_ratio_high",
                        "message": f"Velkasuhde on korkea: {debt_ratio:.1%}",
                        "priority": "high",
                        "action_required": "Harkitse velkojen maksamista"
                    })
            
            # Check emergency fund
            if protection.protection_type == ProtectionType.EMERGENCY_FUND:
                if user_id in self.emergency_funds:
                    emergency_fund = self.emergency_funds[user_id]
                    if emergency_fund.completion_percentage < 25:
                        alerts.append({
                            "type": "emergency_fund_low",
                            "message": f"Hätävaran edistyminen: {emergency_fund.completion_percentage:.1f}%",
                            "priority": "medium",
                            "action_required": "Lisää hätävaran rakentamista"
                        })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to check protection alerts: {e}")
            return []
    
    async def _publish_alerts(self, user_id: int, alerts: List[Dict[str, Any]]):
        """Publish protection alerts"""
        try:
            for alert in alerts:
                await publish_event(
                    EventType.SHIELD_ALERT,
                    user_id,
                    alert,
                    "financial_shield"
                )
                
                # Store alert history
                if user_id not in self.shield_alerts:
                    self.shield_alerts[user_id] = []
                
                alert["timestamp"] = datetime.now().isoformat()
                self.shield_alerts[user_id].append(alert)
                
        except Exception as e:
            logger.error(f"Failed to publish alerts: {e}")
    
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
                6: "Säästöt",
                7: "Vuokra",
                8: "Sähkö",
                9: "Luottokortti"
            }
            return category_names.get(category_id, f"Kategoria {category_id}")
        except Exception as e:
            logger.error(f"Failed to get category name: {e}")
            return f"Kategoria {category_id}"
    
    def _generate_activation_message(self, protection_type: ProtectionType) -> str:
        """Generate activation message"""
        messages = {
            ProtectionType.CRITICAL_EXPENSES: "🛡️ Kriittisten kulujen suoja aktivoitu! Rahasi ovat nyt turvassa.",
            ProtectionType.EMERGENCY_FUND: "💰 Hätävaran rakentaminen aloitettu! Tavoite: 6 kuukauden kulut.",
            ProtectionType.DEBT_PROTECTION: "🚨 Velkavalvonta aktivoitu! Saat varoitukset ennen ongelmia.",
            ProtectionType.INCOME_PROTECTION: "💼 Tulojen suoja aktivoitu! Kehitämme sivutuloja.",
            ProtectionType.INSURANCE_OPTIMIZATION: "📋 Vakuutusten optimointi aktivoitu! Seuraamme kattavuutta."
        }
        return messages.get(protection_type, "🛡️ Taloudellinen suoja aktivoitu!")
    
    def _generate_next_steps(self, protection_type: ProtectionType) -> List[str]:
        """Generate next steps for protection"""
        steps = {
            ProtectionType.CRITICAL_EXPENSES: [
                "Aseta automaattinen siirto kriittisten kulujen tilille",
                "Seuraa kulujasi tarkasti",
                "Harkitse kulujen optimointia"
            ],
            ProtectionType.EMERGENCY_FUND: [
                "Aseta kuukausittainen siirto hätävaratilille",
                "Älä käytä hätävaraa muuhun kuin hätätilanteisiin",
                "Tavoittele 6 kuukauden kulut"
            ],
            ProtectionType.DEBT_PROTECTION: [
                "Seuraa velkasuhdetta kuukausittain",
                "Maksa korkeakorkoiset velat ensin",
                "Vältä uusia velkoja"
            ],
            ProtectionType.INCOME_PROTECTION: [
                "Kehitä sivutuloja",
                "Diversifioi tulolähteitä",
                "Rakenna ammatillista verkostoa"
            ],
            ProtectionType.INSURANCE_OPTIMIZATION: [
                "Arvioi vakuutustarpeet vuosittain",
                "Vertaa vakuutustarjouksia",
                "Varmista riittävä kattavuus"
            ]
        }
        return steps.get(protection_type, ["Seuraa suosituksia", "Pysy kurissa"])
    
    def _protection_to_dict(self, protection: ShieldProtection) -> Dict[str, Any]:
        """Convert protection to dictionary"""
        return {
            "protection_type": protection.protection_type.value,
            "is_active": protection.is_active,
            "target_amount": protection.target_amount,
            "current_amount": protection.current_amount,
            "monthly_contribution": protection.monthly_contribution,
            "priority": protection.priority,
            "description": protection.description,
            "last_updated": protection.last_updated.isoformat(),
            "progress_percentage": (protection.current_amount / protection.target_amount) * 100 if protection.target_amount > 0 else 0
        }
    
    def _emergency_fund_to_dict(self, emergency_fund: Optional[EmergencyFund]) -> Optional[Dict[str, Any]]:
        """Convert emergency fund to dictionary"""
        if not emergency_fund:
            return None
        
        return {
            "target_months": emergency_fund.target_months,
            "monthly_expenses": emergency_fund.monthly_expenses,
            "target_amount": emergency_fund.target_amount,
            "current_amount": emergency_fund.current_amount,
            "contribution_rate": emergency_fund.contribution_rate,
            "completion_percentage": emergency_fund.completion_percentage,
            "estimated_completion_date": emergency_fund.estimated_completion_date.isoformat()
        }
    
    def get_protection_status(self, user_id: int) -> Dict[str, Any]:
        """Get user's protection status"""
        try:
            protections = self.user_protections.get(user_id, {})
            emergency_fund = self.emergency_funds.get(user_id)
            alerts = self.shield_alerts.get(user_id, [])
            
            return {
                "status": "success",
                "active_protections": len(protections),
                "protections": [self._protection_to_dict(p) for p in protections.values()],
                "emergency_fund": self._emergency_fund_to_dict(emergency_fund),
                "recent_alerts": alerts[-5:],  # Last 5 alerts
                "total_alerts": len(alerts)
            }
            
        except Exception as e:
            logger.error(f"Failed to get protection status: {e}")
            return {"status": "error", "message": str(e)}

# Global financial shield instance
financial_shield = FinancialShield() 