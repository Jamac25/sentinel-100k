#!/usr/bin/env python3
"""
🧠 INTELLIGENT BUDGET SYSTEM DEMO
Näyttää miten 100% älykäs budjetti toimii integroituna
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random

class IntelligentBudgetSystem:
    """100% Älykäs budjettijärjestelmä"""
    
    def __init__(self):
        # AI-palvelut
        self.learning = MockLearningEngine()
        self.watchdog = MockWatchdog()
        self.ideas = MockIdeaEngine()
        self.chat = MockAIChat()
        self.automation = MockAutomationEngine()
        
        # Budjetti data
        self.budget = {
            "housing": {"limit": 800, "spent": 650, "adaptive": True},
            "food": {"limit": 400, "spent": 180, "adaptive": True},
            "transport": {"limit": 150, "spent": 80, "adaptive": True},
            "entertainment": {"limit": 200, "spent": 150, "adaptive": True},
            "other": {"limit": 100, "spent": 30, "adaptive": True}
        }
        
        self.total_budget = 1650
        self.mode = "intelligent"  # vs. "static"
        
    async def process_expense(self, expense: Dict[str, Any]):
        """Älykäs kulun käsittely - KAIKKI PALVELUT REAGOIVAT"""
        
        print(f"\n💳 UUSI KULU: {expense['amount']}€ ({expense['category']})")
        print(f"   Kuvaus: {expense['description']}")
        print("="*60)
        
        # 1. LEARNING ANALYSOI KONTEKSTI
        context = await self.learning.analyze_expense_context(expense)
        print(f"\n🧠 LEARNING ENGINE:")
        print(f"   - Normaali kulu tälle päivälle: {context['normal_for_day']}€")
        print(f"   - Poikkeama: {context['deviation']}%")
        print(f"   - Trendi: {context['trend']}")
        
        # 2. ENNUSTA KUUKAUDEN LOPPU
        prediction = await self.learning.predict_month_end(expense)
        print(f"\n📊 ENNUSTE:")
        print(f"   - Budjetti loppuu: {prediction['budget_end_day']}. päivä")
        print(f"   - Ylitys: {prediction['overspend_amount']}€")
        print(f"   - Todennäköisyys: {prediction['probability']}%")
        
        # 3. WATCHDOG TARKISTAA RISKIT
        risk = await self.watchdog.assess_budget_risk(expense, prediction)
        print(f"\n🚨 WATCHDOG:")
        print(f"   - Riskitaso: {risk['level']} ({risk['score']}/10)")
        print(f"   - Moodi: {risk['mode']}")
        
        # 4. AUTOMAATTISET TOIMET
        if risk['score'] > 7:
            print(f"\n⚡ AUTOMAATTISET TOIMET:")
            
            # Säädä budjettia
            adjustments = await self.auto_adjust_budget(expense, prediction)
            for adj in adjustments:
                print(f"   ✓ {adj}")
            
            # IdeaEngine generoi tuloja
            if prediction['overspend_amount'] > 100:
                ideas = await self.ideas.emergency_income_ideas(
                    amount_needed=prediction['overspend_amount'],
                    timeframe='this_week'
                )
                print(f"\n💡 IDEAENGINE - Pikatulot:")
                for idea in ideas[:3]:
                    print(f"   • {idea['title']} (+{idea['potential']}€)")
            
            # Automation lukitsee kategorioita
            locked = await self.automation.lock_risky_categories(risk)
            if locked:
                print(f"\n🔒 AUTOMATION:")
                for cat in locked:
                    print(f"   ✓ {cat} lukittu loppukuuksi")
        
        # 5. CHAT SELITTÄÄ KÄYTTÄJÄLLE
        explanation = await self.chat.explain_situation(expense, context, prediction, risk)
        print(f"\n💬 AI CHAT:")
        print(f"   {explanation}")
        
        # 6. PÄIVITÄ BUDJETTI
        self.budget[expense['category']]['spent'] += expense['amount']
        
        print("\n" + "="*60)
        await self.show_intelligent_status()
        
    async def auto_adjust_budget(self, expense, prediction):
        """Automaattiset budjetin säädöt"""
        adjustments = []
        
        # Laske uudet päivärajat
        days_left = 30 - datetime.now().day
        for category, data in self.budget.items():
            if data['adaptive']:
                remaining = data['limit'] - data['spent']
                new_daily = remaining / days_left * 0.8  # 80% tiukempi
                
                adjustments.append(
                    f"{category}: {remaining/days_left:.1f}€/pv → {new_daily:.1f}€/pv"
                )
        
        return adjustments
    
    async def show_intelligent_status(self):
        """Näytä älykäs budjettistatus"""
        print("\n📊 ÄLYKÄS BUDJETTISTATUS:")
        
        total_spent = sum(cat['spent'] for cat in self.budget.values())
        usage = (total_spent / self.total_budget) * 100
        
        print(f"Kokonaiskäyttö: {total_spent:.0f}€ / {self.total_budget}€ ({usage:.0f}%)")
        
        # Näytä kategoriat älykkäästi
        for category, data in self.budget.items():
            cat_usage = (data['spent'] / data['limit']) * 100
            status = self.get_smart_status(cat_usage, category)
            print(f"{category:15} {data['spent']:>6.0f}€/{data['limit']}€ {status}")

    def get_smart_status(self, usage, category):
        """Älykäs statusteksti"""
        if usage > 90:
            return f"🔴 KRIITTINEN ({usage:.0f}%)"
        elif usage > 75:
            return f"🟡 Varoitus ({usage:.0f}%)"
        elif usage > 50:
            return f"🟢 OK ({usage:.0f}%)"
        else:
            return f"✅ Erinomainen ({usage:.0f}%)"

# Mock AI-palvelut
class MockLearningEngine:
    async def analyze_expense_context(self, expense):
        # Simuloi kontekstianalyysi
        normal = expense['amount'] * 0.6
        return {
            'normal_for_day': normal,
            'deviation': ((expense['amount'] - normal) / normal * 100),
            'trend': 'increasing' if expense['amount'] > normal else 'stable'
        }
    
    async def predict_month_end(self, expense):
        # Simuloi ennuste
        return {
            'budget_end_day': random.randint(15, 25),
            'overspend_amount': random.randint(50, 300),
            'probability': random.randint(60, 95)
        }

class MockWatchdog:
    async def assess_budget_risk(self, expense, prediction):
        score = min(10, prediction['overspend_amount'] / 50 + 5)
        return {
            'score': score,
            'level': 'HIGH' if score > 7 else 'MEDIUM' if score > 5 else 'LOW',
            'mode': 'EMERGENCY' if score > 8 else 'ALERT' if score > 6 else 'ACTIVE'
        }

class MockIdeaEngine:
    async def emergency_income_ideas(self, amount_needed, timeframe):
        return [
            {'title': 'Kiire-freelance projekti', 'potential': amount_needed * 0.6},
            {'title': 'Myy tarpeettomia tavaroita', 'potential': amount_needed * 0.3},
            {'title': 'Wolt-kuljetus iltaisin', 'potential': amount_needed * 0.4}
        ]

class MockAIChat:
    async def explain_situation(self, expense, context, prediction, risk):
        if risk['score'] > 7:
            return (
                f"Huomasin {expense['amount']}€ kulun - se on {context['deviation']:.0f}% "
                f"normaalia suurempi. Nykyisellä tahdilla budjetti loppuu {prediction['budget_end_day']}. päivä. "
                f"Säädin automaattisesti päivärajojasi ja ehdotin tapoja tienata {prediction['overspend_amount']}€ "
                f"tässä kuussa. Pysyt tavoitteessa jos seuraat uusia rajoja!"
            )
        else:
            return "Kulu kirjattu. Budjettitilanteesi on hyvä!"

class MockAutomationEngine:
    async def lock_risky_categories(self, risk):
        if risk['score'] > 8:
            return ['entertainment', 'other']
        elif risk['score'] > 6:
            return ['entertainment']
        return []

# DEMO
async def run_intelligent_budget_demo():
    """Aja älykäs budjettidemo"""
    
    print("🧠 INTELLIGENT BUDGET SYSTEM DEMO")
    print("="*60)
    
    budget = IntelligentBudgetSystem()
    
    # Näytä alkutilanne
    print("\n📊 ALKUTILANNE (10. päivä kuussa):")
    await budget.show_intelligent_status()
    
    # Simuloi kuluja
    expenses = [
        {
            'amount': 45.50,
            'category': 'food',
            'description': 'Lounas ravintolassa',
            'timestamp': datetime.now()
        },
        {
            'amount': 89.90,
            'category': 'entertainment',
            'description': 'Konserttilippu',
            'timestamp': datetime.now()
        },
        {
            'amount': 250.00,
            'category': 'food',
            'description': 'Viikon ruokaostokset + juhlat',
            'timestamp': datetime.now()
        }
    ]
    
    # Käsittele kulut
    for expense in expenses:
        await asyncio.sleep(2)  # Simuloi viivettä
        await budget.process_expense(expense)
    
    print("\n🎯 YHTEENVETO:")
    print("Budget System reagoi ÄLYKKÄÄSTI:")
    print("✓ Oppi kulutuskäyttäytymisestä")
    print("✓ Ennusti budjetin loppumisen")
    print("✓ Sääti rajoja automaattisesti")
    print("✓ Generoi lisätulomahdollisuuksia")
    print("✓ Lukitsi riskirategoriat")
    print("✓ Selitti tilanteen käyttäjälle")
    print("\n💡 Tämä on 100% älykäs budjetti!")

if __name__ == "__main__":
    asyncio.run(run_intelligent_budget_demo()) 