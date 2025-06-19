"""
Liabilities Insight™ - Velkakäyttäytymisen seuranta ja optimointi
Analysoi lainoja, luottoja ja velkoja, luo maksusuunnitelmat ja optimoi korkomenoja
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.category import Category
import logging
import numpy as np
import pandas as pd
from collections import defaultdict
import statistics
import math

logger = logging.getLogger(__name__)

class Liability:
    """Yksittäinen velka/laina"""
    
    def __init__(self, name: str, liability_type: str):
        self.name = name
        self.type = liability_type  # mortgage, loan, credit_card, installment, other
        self.principal_balance = 0.0
        self.interest_rate = 0.0
        self.monthly_payment = 0.0
        self.minimum_payment = 0.0
        self.payments = []  # Lista maksuista
        self.payment_dates = []
        self.interest_paid_total = 0.0
        self.payment_history_months = 0
        self.payment_consistency = 0.0
        self.overpayment_potential = 0.0
        
    def add_payment(self, amount: float, date: datetime, is_interest: bool = False):
        """Lisää maksu"""
        self.payments.append(amount)
        self.payment_dates.append(date)
        if is_interest:
            self.interest_paid_total += amount
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Laske velan mittarit"""
        if not self.payments:
            return
            
        self.monthly_payment = statistics.mean(self.payments) if self.payments else 0
        self.payment_history_months = len(self.payments)
        
        # Maksutapojen johdonmukaisuus
        if len(self.payments) > 1:
            payment_variance = statistics.stdev(self.payments) / statistics.mean(self.payments)
            self.payment_consistency = max(0, 1.0 - payment_variance)
        
        # Ylimaksujen potentiaali
        if self.minimum_payment > 0 and self.monthly_payment > self.minimum_payment:
            self.overpayment_potential = self.monthly_payment - self.minimum_payment

class LiabilitiesInsight:
    """
    Liabilities Insight™ - Velkakäyttäytymisen seuranta
    
    Analysoi:
    - Kaikki velat ja lainat
    - Korkomenot ja niiden optimointi
    - Maksusuunnitelmat
    - Todellinen nettoedistymä 100k€ tavoitteeseen
    """
    
    def __init__(self):
        self.liabilities = {}  # user_id -> List[Liability]
        self.debt_categories = {
            'mortgage': ['asuntolaina', 'mortgage', 'kiinnitys', 'hypoteekkil'],
            'loan': ['laina', 'loan', 'pankkilaina', 'kulutusluotto'],
            'credit_card': ['luottokortti', 'credit card', 'visa', 'mastercard', 'amex'],
            'installment': ['osamaksu', 'installment', 'erämaksu', 'maksuerä'],
            'interest': ['korko', 'interest', 'viivästyskorko', 'luottokorkokulut']
        }
        
        # Suomalaiset keskikorot (2024)
        self.average_interest_rates = {
            'mortgage': 4.5,
            'loan': 8.5,
            'credit_card': 15.0,
            'installment': 12.0,
            'other': 10.0
        }
    
    def analyze_liabilities(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Analysoi käyttäjän velat ja velvoitteet"""
        try:
            # Hae velkaan liittyvät transaktiot
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # 12 kuukautta
            
            debt_transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0  # Menot (maksut)
            ).all()
            
            # Suodata velkamaksut
            debt_payments = self._filter_debt_transactions(debt_transactions)
            
            if not debt_payments:
                return {
                    "status": "no_debt_data",
                    "message": "Ei velkamaksuja löydetty",
                    "debt_free_status": True,
                    "recommendations": self._get_debt_free_recommendations()
                }
            
            # Analysoi velat
            liabilities = self._analyze_debt_structure(debt_payments)
            self.liabilities[user_id] = liabilities
            
            # Laske kokonaisanalyysi
            analysis = self._calculate_debt_analysis(liabilities)
            
            # Luo optimointisuunnitelma
            optimization_plan = self._create_debt_optimization_plan(liabilities)
            
            # Laske todellinen nettoedistymä
            net_progress = self._calculate_net_progress_to_goal(user_id, db, analysis)
            
            return {
                "status": "success",
                "debt_analysis": analysis,
                "liabilities": [self._liability_to_dict(liability) for liability in liabilities],
                "optimization_plan": optimization_plan,
                "net_progress_to_goal": net_progress,
                "total_liabilities": len(liabilities)
            }
            
        except Exception as e:
            logger.error(f"Virhe velka-analyysissä: {e}")
            return {"status": "error", "message": str(e)}
    
    def _filter_debt_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Suodata velkamaksut transaktioista"""
        debt_transactions = []
        
        for t in transactions:
            description = (t.description or "").lower()
            
            # Tarkista onko velkamaksu kuvauksen perusteella
            is_debt = False
            for debt_type, keywords in self.debt_categories.items():
                if any(keyword in description for keyword in keywords):
                    is_debt = True
                    break
            
            # Lisää myös suuret säännölliset maksut (todennäköisesti lainoja)
            if not is_debt and t.amount > 200:  # Yli 200€ maksut
                # Tarkista onko säännöllinen (sama summa useita kertoja)
                similar_transactions = [tx for tx in transactions 
                                      if abs(tx.amount - t.amount) < 10 and tx.id != t.id]
                if len(similar_transactions) >= 2:
                    is_debt = True
            
            if is_debt:
                debt_transactions.append(t)
        
        return debt_transactions
    
    def _analyze_debt_structure(self, debt_transactions: List[Transaction]) -> List[Liability]:
        """Analysoi velkarakenne transaktioista"""
        liabilities = []
        
        # Ryhmittele samankaltaiset maksut
        payment_groups = defaultdict(list)
        
        for t in debt_transactions:
            # Luokittele velkatyyppi
            debt_type = self._classify_debt_type(t.description or "")
            
            # Ryhmittele summan ja tyypin mukaan
            group_key = f"{debt_type}_{int(t.amount/10)*10}"  # Pyöristä lähimpään 10€
            payment_groups[group_key].append(t)
        
        # Luo Liability-objektit
        for group_key, transactions in payment_groups.items():
            if len(transactions) >= 2:  # Vähintään 2 maksua
                debt_type = group_key.split('_')[0]
                liability = Liability(f"{debt_type}_debt_{len(liabilities)+1}", debt_type)
                
                for t in transactions:
                    is_interest = 'korko' in (t.description or "").lower()
                    liability.add_payment(t.amount, t.transaction_date, is_interest)
                
                # Arvioi lainan tiedot
                self._estimate_loan_details(liability)
                liabilities.append(liability)
        
        return liabilities
    
    def _classify_debt_type(self, description: str) -> str:
        """Luokittele velan tyyppi"""
        desc_lower = description.lower()
        
        for debt_type, keywords in self.debt_categories.items():
            if any(keyword in desc_lower for keyword in keywords):
                return debt_type
        
        return 'other'
    
    def _estimate_loan_details(self, liability: Liability):
        """Arvioi lainan tiedot maksuhistorian perusteella"""
        if not liability.payments:
            return
        
        # Arvioi kuukausimaksu
        liability.monthly_payment = statistics.mean(liability.payments)
        liability.minimum_payment = min(liability.payments) if liability.payments else 0
        
        # Arvioi korko keskimääräisen mukaan
        liability.interest_rate = self.average_interest_rates.get(liability.type, 10.0)
        
        # Arvioi jäljellä oleva pääoma (yksinkertainen arvio)
        # Oletetaan että 70% maksusta menee pääomaan, 30% korkoon
        principal_payment = liability.monthly_payment * 0.7
        months_remaining = 60  # Oletus: 5 vuotta jäljellä
        liability.principal_balance = principal_payment * months_remaining
    
    def _calculate_debt_analysis(self, liabilities: List[Liability]) -> Dict[str, Any]:
        """Laske kokonaisvaltainen velka-analyysi"""
        if not liabilities:
            return {"total_debt": 0, "monthly_payments": 0, "status": "debt_free"}
        
        total_debt = sum(l.principal_balance for l in liabilities)
        total_monthly_payments = sum(l.monthly_payment for l in liabilities)
        total_interest_paid = sum(l.interest_paid_total for l in liabilities)
        
        # Laske keskimääräinen korko
        weighted_interest_rate = 0
        if total_debt > 0:
            for liability in liabilities:
                weight = liability.principal_balance / total_debt
                weighted_interest_rate += liability.interest_rate * weight
        
        # Arvioi vuotuiset korkomenot
        annual_interest_cost = total_debt * (weighted_interest_rate / 100)
        
        # Velka-tulo-suhde (oletetaan 3000€ kuukausitulo)
        estimated_monthly_income = 3000  # Tämä pitäisi saada tuloanalyysissä
        debt_to_income_ratio = (total_monthly_payments / estimated_monthly_income) * 100
        
        # Määritä velkatilanne
        if debt_to_income_ratio > 40:
            debt_status = "critical"
        elif debt_to_income_ratio > 25:
            debt_status = "concerning"
        elif debt_to_income_ratio > 15:
            debt_status = "moderate"
        else:
            debt_status = "manageable"
        
        return {
            "total_debt": total_debt,
            "monthly_payments": total_monthly_payments,
            "annual_interest_cost": annual_interest_cost,
            "weighted_interest_rate": weighted_interest_rate,
            "debt_to_income_ratio": debt_to_income_ratio,
            "debt_status": debt_status,
            "total_interest_paid": total_interest_paid,
            "debt_types": list(set(l.type for l in liabilities)),
            "payment_consistency": statistics.mean([l.payment_consistency for l in liabilities]) if liabilities else 0
        }
    
    def _create_debt_optimization_plan(self, liabilities: List[Liability]) -> Dict[str, Any]:
        """Luo velkojen optimointisuunnitelma"""
        if not liabilities:
            return {"status": "no_debt"}
        
        # Järjestä velat korkojen mukaan (korkein ensin)
        sorted_by_interest = sorted(liabilities, key=lambda x: x.interest_rate, reverse=True)
        
        # Järjestä velat saldon mukaan (pienin ensin - "lumipallo"-metodi)
        sorted_by_balance = sorted(liabilities, key=lambda x: x.principal_balance)
        
        optimization_strategies = []
        
        # Strategia 1: Korkeimmat korot ensin
        high_interest_debt = [l for l in liabilities if l.interest_rate > 10]
        if high_interest_debt:
            optimization_strategies.append({
                "strategy": "avalanche_method",
                "name": "Korkeimmat korot ensin",
                "priority": "high",
                "target_debts": [l.name for l in high_interest_debt],
                "potential_savings": self._calculate_interest_savings(high_interest_debt),
                "description": "Maksa ensin velat joissa korkein korko - säästää eniten rahaa"
            })
        
        # Strategia 2: Pienimmät saldot ensin (lumipallo)
        if len(liabilities) > 1:
            smallest_debts = sorted_by_balance[:2]
            optimization_strategies.append({
                "strategy": "snowball_method", 
                "name": "Lumipallo-metodi",
                "priority": "medium",
                "target_debts": [l.name for l in smallest_debts],
                "psychological_benefit": "Nopeat voitot motivoivat",
                "description": "Maksa ensin pienimmät velat - antaa psykologista boost"
            })
        
        # Strategia 3: Ylimaksut
        overpayment_potential = sum(l.overpayment_potential for l in liabilities)
        if overpayment_potential > 50:
            optimization_strategies.append({
                "strategy": "overpayment_optimization",
                "name": "Ylimaksujen optimointi", 
                "priority": "medium",
                "current_overpayment": overpayment_potential,
                "recommendation": "Keskitä ylimaksut korkeimpikorkoisiin velkoihin",
                "description": f"Käytät jo {overpayment_potential:.0f}€/kk ylimaksuihin - optimoi kohdentaminen"
            })
        
        # Strategia 4: Jälleenrahoitus
        refinancing_candidates = [l for l in liabilities if l.interest_rate > 8 and l.principal_balance > 5000]
        if refinancing_candidates:
            optimization_strategies.append({
                "strategy": "refinancing",
                "name": "Jälleenrahoitus",
                "priority": "high" if any(l.interest_rate > 12 for l in refinancing_candidates) else "medium",
                "candidates": [l.name for l in refinancing_candidates],
                "potential_rate_reduction": "2-5 prosenttiyksikköä",
                "description": "Harkitse lainojen yhdistämistä tai uudelleenrahoitusta"
            })
        
        return {
            "status": "success",
            "optimization_strategies": optimization_strategies,
            "recommended_order": [s["name"] for s in sorted(optimization_strategies, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)],
            "total_potential_savings": sum(s.get("potential_savings", 0) for s in optimization_strategies)
        }
    
    def _calculate_interest_savings(self, high_interest_debts: List[Liability]) -> float:
        """Laske mahdolliset korkosäästöt"""
        total_savings = 0
        for debt in high_interest_debts:
            # Yksinkertainen arvio: jos korko laskisi 3 prosenttiyksikköä
            annual_savings = debt.principal_balance * 0.03
            total_savings += annual_savings
        return total_savings
    
    def _calculate_net_progress_to_goal(self, user_id: int, db: Session, debt_analysis: Dict) -> Dict[str, Any]:
        """Laske todellinen nettoedistymä 100k€ tavoitteeseen"""
        try:
            # Hae säästöt viimeiseltä 6 kuukaudelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            savings_transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount < 0  # Tulot
            ).all()
            
            expense_transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0  # Menot
            ).all()
            
            # Laske kuukausittaiset nettosäästöt
            monthly_income = abs(sum(t.amount for t in savings_transactions)) / 6
            monthly_expenses = sum(t.amount for t in expense_transactions) / 6
            monthly_debt_payments = debt_analysis.get("monthly_payments", 0)
            
            # Todellinen nettosäästö (tulot - menot - velkojen lyhennykset)
            net_monthly_savings = monthly_income - monthly_expenses
            
            # Velkojen lyhennykset vähentävät käytettävissä olevia säästöjä
            available_for_goal = net_monthly_savings - (monthly_debt_payments * 0.7)  # 70% menee pääomaan
            
            # Arvio 100k€ tavoitteeseen
            months_to_goal = 100000 / available_for_goal if available_for_goal > 0 else float('inf')
            
            # Korkomenojen vaikutus tavoitteeseen
            annual_interest_cost = debt_analysis.get("annual_interest_cost", 0)
            interest_impact_on_goal = annual_interest_cost * 5  # 5 vuoden korkomenot
            
            return {
                "net_monthly_savings": net_monthly_savings,
                "monthly_debt_payments": monthly_debt_payments,
                "available_for_goal": available_for_goal,
                "months_to_goal": months_to_goal if months_to_goal != float('inf') else None,
                "debt_impact_on_goal": {
                    "annual_interest_cost": annual_interest_cost,
                    "five_year_interest_cost": interest_impact_on_goal,
                    "goal_delay_months": interest_impact_on_goal / available_for_goal if available_for_goal > 0 else 0
                },
                "recommendations": self._get_net_progress_recommendations(available_for_goal, debt_analysis)
            }
            
        except Exception as e:
            logger.error(f"Virhe nettoedistymisen laskennassa: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_net_progress_recommendations(self, available_for_goal: float, debt_analysis: Dict) -> List[str]:
        """Suositukset nettoedistymän parantamiseksi"""
        recommendations = []
        
        if available_for_goal < 500:
            recommendations.append("🚨 Velkojen maksut rajoittavat merkittävästi säästöjäsi")
            recommendations.append("Priorisoi velkojen maksaminen ennen 100k€ tavoitetta")
        
        debt_status = debt_analysis.get("debt_status", "manageable")
        if debt_status in ["critical", "concerning"]:
            recommendations.append("Velkatilanne on huolestuttava - keskity ensin velkojen hoitoon")
            recommendations.append("Harkitse velkaneuvojan konsultointia")
        
        annual_interest = debt_analysis.get("annual_interest_cost", 0)
        if annual_interest > 2000:
            recommendations.append(f"Maksat {annual_interest:.0f}€/vuosi korkoja - optimoi velkojen korot")
            recommendations.append("Jälleenrahoitus voisi säästää merkittävästi")
        
        if available_for_goal > 0:
            recommendations.append(f"Käytettävissä 100k€ tavoitteeseen: {available_for_goal:.0f}€/kk")
        
        return recommendations
    
    def _get_debt_free_recommendations(self) -> List[str]:
        """Suositukset velattomille"""
        return [
            "🎉 Loistavaa! Sinulla ei ole merkittäviä velkoja",
            "Voit keskittyä täysimääräisesti 100k€ säästötavoitteeseen",
            "Harkitse sijoittamista korkeamman tuoton saamiseksi",
            "Pidä hyvä luottotieto välttämällä tarpeetonta velkaantumista"
        ]
    
    def _liability_to_dict(self, liability: Liability) -> Dict[str, Any]:
        """Muunna Liability dictionary:ksi"""
        return {
            "name": liability.name,
            "type": liability.type,
            "principal_balance": liability.principal_balance,
            "interest_rate": liability.interest_rate,
            "monthly_payment": liability.monthly_payment,
            "minimum_payment": liability.minimum_payment,
            "payment_consistency": liability.payment_consistency,
            "overpayment_potential": liability.overpayment_potential,
            "interest_paid_total": liability.interest_paid_total,
            "payment_history_months": liability.payment_history_months
        }
    
    def get_debt_payoff_calculator(self, liability_data: Dict[str, Any], extra_payment: float = 0) -> Dict[str, Any]:
        """Laske velan maksusuunnitelma"""
        try:
            principal = liability_data.get("principal_balance", 0)
            annual_rate = liability_data.get("interest_rate", 10) / 100
            monthly_payment = liability_data.get("monthly_payment", 0)
            
            if principal <= 0 or monthly_payment <= 0:
                return {"status": "invalid_data"}
            
            monthly_rate = annual_rate / 12
            total_payment = monthly_payment + extra_payment
            
            # Laske maksukuukaudet
            if monthly_rate > 0:
                months = math.log(1 + (principal * monthly_rate) / total_payment) / math.log(1 + monthly_rate)
            else:
                months = principal / total_payment
            
            months = max(1, math.ceil(months))
            
            # Laske kokonaiskorkomenot
            total_paid = total_payment * months
            total_interest = total_paid - principal
            
            # Vertailu ilman ylimaksuja
            if extra_payment > 0:
                months_without_extra = math.log(1 + (principal * monthly_rate) / monthly_payment) / math.log(1 + monthly_rate)
                months_without_extra = max(1, math.ceil(months_without_extra))
                interest_without_extra = (monthly_payment * months_without_extra) - principal
                
                savings = {
                    "months_saved": months_without_extra - months,
                    "interest_saved": interest_without_extra - total_interest
                }
            else:
                savings = None
            
            return {
                "status": "success",
                "months_to_payoff": months,
                "total_interest": total_interest,
                "total_amount_paid": total_paid,
                "monthly_payment_with_extra": total_payment,
                "savings_from_extra_payment": savings
            }
            
        except Exception as e:
            logger.error(f"Virhe maksusuunnitelman laskennassa: {e}")
            return {"status": "error", "message": str(e)} 