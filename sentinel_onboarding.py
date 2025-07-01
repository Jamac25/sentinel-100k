#!/usr/bin/env python3

"""
🎯 SENTINEL 100K - ONBOARDING SYSTEM
===================================

Tervetuloa Sentinel 100K:hon! 
Henkilökohtainen rahoitusagenttisi 100,000€ säästötavoitteeseen.

Tämä onboarding kerää oikeat tietosi ja luo sinulle henkilökohtaisen
rahoitusprofiilin ja tavoitteet.

python3 sentinel_onboarding.py
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import re

class SentinelOnboarding:
    def __init__(self):
        self.user_data = {}
        self.financial_data = {}
        self.goals = []
        self.transactions = []
        
    def print_header(self):
        """Print Sentinel welcome header"""
        print("\n" + "="*60)
        print("🛡️  SENTINEL 100K - HENKILÖKOHTAINEN RAHOITUSAGENTTI")
        print("="*60)
        print("🎯 Tavoite: 100,000€ säästöt")
        print("🤖 AI-avusteinen rahoituksen hallinta")
        print("📊 Reaaliaikainen seuranta ja neuvonta")
        print("="*60)
        print()
        
    def get_user_input(self, prompt: str, input_type: str = "text", optional: bool = False) -> Any:
        """Get user input with validation"""
        while True:
            try:
                value = input(f"📝 {prompt}: ").strip()
                
                if not value and optional:
                    return None
                    
                if not value:
                    print("❌ Tämä tieto vaaditaan. Yritä uudelleen.")
                    continue
                
                if input_type == "number":
                    # Allow comma as decimal separator (Finnish style)
                    value = value.replace(",", ".")
                    return float(value)
                elif input_type == "int":
                    return int(value)
                elif input_type == "email":
                    if "@" in value and "." in value:
                        return value
                    else:
                        print("❌ Anna kelvollinen sähköpostiosoite.")
                        continue
                elif input_type == "yes_no":
                    if value.lower() in ['k', 'kyllä', 'y', 'yes', 'joo']:
                        return True
                    elif value.lower() in ['e', 'ei', 'n', 'no']:
                        return False
                    else:
                        print("❌ Vastaa 'k' (kyllä) tai 'e' (ei).")
                        continue
                        
                return value
                
            except ValueError:
                print(f"❌ Anna {input_type} muodossa oleva arvo.")
                continue
    
    def collect_personal_info(self):
        """Collect personal information"""
        print("👤 HENKILÖTIEDOT")
        print("-" * 20)
        
        self.user_data = {
            "name": self.get_user_input("Nimi (etunimi riittää)"),
            "email": self.get_user_input("Sähköposti", "email", optional=True),
            "age": self.get_user_input("Ikä", "int", optional=True),
            "location": self.get_user_input("Asuinpaikka (kaupunki)", optional=True),
            "profession": self.get_user_input("Ammatti/työ", optional=True)
        }
        
        print(f"\n✅ Tervetuloa {self.user_data['name']}! 👋")
        
    def collect_financial_status(self):
        """Collect current financial status"""
        print("\n💰 NYKYINEN TALOUSTILANNE")
        print("-" * 30)
        
        print("💡 Näitä tietoja käytetään henkilökohtaisen suunnitelman tekemiseen.")
        print("   Kaikki tiedot säilytetään turvallisesti vain omalla koneellasi.\n")
        
        # Current savings
        current_savings = self.get_user_input(
            "Nykyiset säästöt (€, esim. 5000 tai 5000,50)", 
            "number"
        )
        
        # Monthly income
        monthly_income = self.get_user_input(
            "Kuukausitulot brutto (€)", 
            "number"
        )
        
        # Monthly expenses
        print("\n📋 Kuukausittaiset menot (arviot riittävät):")
        
        rent = self.get_user_input("  • Vuokra/asumiskulut (€)", "number")
        food = self.get_user_input("  • Ruoka ja päivittäistavarat (€)", "number")
        transport = self.get_user_input("  • Liikenne (€)", "number", optional=True) or 0
        utilities = self.get_user_input("  • Sähkö, netti, puhelin (€)", "number", optional=True) or 0
        entertainment = self.get_user_input("  • Viihde ja harrastukset (€)", "number", optional=True) or 0
        other = self.get_user_input("  • Muut menot (€)", "number", optional=True) or 0
        
        total_expenses = rent + food + transport + utilities + entertainment + other
        net_monthly = monthly_income - total_expenses
        
        self.financial_data = {
            "current_savings": current_savings,
            "monthly_income": monthly_income,
            "monthly_expenses": {
                "rent": rent,
                "food": food,
                "transport": transport,
                "utilities": utilities,
                "entertainment": entertainment,
                "other": other,
                "total": total_expenses
            },
            "monthly_net": net_monthly,
            "savings_rate": (net_monthly / monthly_income * 100) if monthly_income > 0 else 0
        }
        
        print(f"\n📊 YHTEENVETO:")
        print(f"   💵 Kuukausitulot: {monthly_income:,.0f}€")
        print(f"   💸 Kuukausimenot: {total_expenses:,.0f}€")
        print(f"   💰 Kuukausisäästö: {net_monthly:,.0f}€")
        print(f"   📈 Säästöaste: {self.financial_data['savings_rate']:.1f}%")
        
        if net_monthly <= 0:
            print(f"\n⚠️  HUOMIO: Menot ylittävät tulot!")
            print("   Sentinel auttaa löytämään säästöjä ja optimoimaan budjettia.")
        elif self.financial_data['savings_rate'] < 10:
            print(f"\n💡 VINKKI: Säästöaste alle 10%. Tavoitellaan vähintään 20%!")
        else:
            print(f"\n🎉 LOISTAVAA! Hyvä säästöaste. Sentinel auttaa optimoimaan entisestään!")
    
    def set_goals(self):
        """Set savings goals"""
        print("\n🎯 SÄÄSTÖTAVOITTEET")
        print("-" * 20)
        
        print("🏆 Sentinel 100K:n päätavoite on 100,000€ säästöt.")
        print("   Luodaan sinulle henkilökohtainen polku sinne!\n")
        
        current = self.financial_data["current_savings"]
        remaining = 100000 - current
        monthly_saving = max(self.financial_data["monthly_net"], 0)
        
        if remaining <= 0:
            print("🎉 ONNITTELUT! Olet jo saavuttanut 100K€ tavoitteen!")
            target_months = 0
        elif monthly_saving <= 0:
            print("📋 Ensin optimoidaan budjetti, jotta säästäminen on mahdollista.")
            target_months = None
        else:
            target_months = remaining / monthly_saving
            target_date = datetime.now() + timedelta(days=target_months * 30)
        
        # Main goal
        main_goal = {
            "id": "main_100k",
            "name": "Hätävara 100K€",
            "description": "Tavoitteena on saavuttaa 100,000€ säästöt taloudellista turvaa varten",
            "target_amount": 100000.0,
            "current_amount": current,
            "progress_percent": (current / 100000 * 100),
            "monthly_target": monthly_saving,
            "estimated_completion": target_date.isoformat() if target_months else None,
            "months_remaining": target_months,
            "status": "active"
        }
        
        self.goals.append(main_goal)
        
        # Intermediate goals
        if remaining > 0:
            # 6 months emergency fund
            emergency_target = self.financial_data["monthly_expenses"]["total"] * 6
            if current < emergency_target:
                emergency_goal = {
                    "id": "emergency_6m",
                    "name": "Hätävara 6kk",
                    "description": f"6 kuukauden menoja vastaava hätävara ({emergency_target:,.0f}€)",
                    "target_amount": emergency_target,
                    "current_amount": min(current, emergency_target),
                    "progress_percent": min(current / emergency_target * 100, 100),
                    "priority": "high",
                    "status": "active" if current < emergency_target else "completed"
                }
                self.goals.append(emergency_goal)
        
        # Custom goal
        custom_goal = self.get_user_input(
            "\nHaluatko asettaa lisätavoitteen? (esim. 'Lomakassa 3000€') [ENTER = ei]",
            optional=True
        )
        
        if custom_goal:
            custom_amount = self.get_user_input(
                f"Paljonko '{custom_goal}' maksaa (€)?", 
                "number"
            )
            
            custom_goal_obj = {
                "id": "custom_1",
                "name": custom_goal,
                "description": f"Henkilökohtainen tavoite: {custom_goal}",
                "target_amount": custom_amount,
                "current_amount": 0,
                "progress_percent": 0,
                "status": "active"
            }
            self.goals.append(custom_goal_obj)
        
        # Show goals summary
        print(f"\n🎯 TAVOITTEESI:")
        for goal in self.goals:
            status_emoji = "🎯" if goal["status"] == "active" else "✅" 
            print(f"   {status_emoji} {goal['name']}: {goal['current_amount']:,.0f}€ / {goal['target_amount']:,.0f}€ ({goal['progress_percent']:.1f}%)")
    
    def create_sample_transactions(self):
        """Create sample transactions based on user data"""
        print("\n📋 Luo näytetransaktioita...")
        
        base_date = datetime.now()
        transactions = []
        
        # Income
        income_transaction = {
            "id": "income_001",
            "amount": self.financial_data["monthly_income"],
            "description": "Palkka",
            "category": "palkka",
            "category_name": "Palkka",
            "type": "income",
            "date": (base_date - timedelta(days=15)).isoformat(),
            "merchant": self.user_data.get("profession", "Työnantaja")
        }
        transactions.append(income_transaction)
        
        # Expenses based on budget
        expenses = [
            ("Vuokra", self.financial_data["monthly_expenses"]["rent"], "asuminen", "Vuokranantaja"),
            ("Ruokaostokset", self.financial_data["monthly_expenses"]["food"] * 0.6, "ruoka", "K-Market"),
            ("Ruokaostokset", self.financial_data["monthly_expenses"]["food"] * 0.4, "ruoka", "Prisma"),
            ("Bussikortti", self.financial_data["monthly_expenses"]["transport"], "liikenne", "HSL"),
            ("Sähkölasku", self.financial_data["monthly_expenses"]["utilities"] * 0.7, "asuminen", "Helen Oy"),
            ("Netflix", min(12.95, self.financial_data["monthly_expenses"]["entertainment"] * 0.3), "viihde", "Netflix"),
        ]
        
        for i, (desc, amount, category, merchant) in enumerate(expenses):
            if amount > 0:
                transaction = {
                    "id": f"expense_{i:03d}",
                    "amount": -amount,
                    "description": desc,
                    "category": category,
                    "category_name": category.title(),
                    "type": "expense",
                    "date": (base_date - timedelta(days=i*2 + 1)).isoformat(),
                    "merchant": merchant
                }
                transactions.append(transaction)
        
        self.transactions = transactions
    
    def save_profile(self):
        """Save user profile to JSON file"""
        profile = {
            "user": {
                **self.user_data,
                "created_at": datetime.now().isoformat(),
                "onboarding_completed": True
            },
            "financial": self.financial_data,
            "goals": self.goals,
            "transactions": self.transactions,
            "settings": {
                "currency": "EUR",
                "language": "fi",
                "notifications": True,
                "ai_coaching": True
            }
        }
        
        with open("sentinel_user_profile.json", "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Profiili tallennettu: sentinel_user_profile.json")
        return profile
    
    def show_welcome_summary(self):
        """Show final welcome summary"""
        name = self.user_data["name"]
        current = self.financial_data["current_savings"]
        monthly = self.financial_data["monthly_net"]
        rate = self.financial_data["savings_rate"]
        
        print(f"\n🎉 TERVETULOA SENTINEL 100K:HON, {name.upper()}!")
        print("="*60)
        print(f"💰 Nykyiset säästösi: {current:,.0f}€")
        print(f"📈 Kuukausisäästö: {monthly:,.0f}€")
        print(f"🎯 Säästöaste: {rate:.1f}%")
        print(f"🏆 Tavoite: 100,000€ ({100000-current:,.0f}€ jäljellä)")
        
        if monthly > 0:
            months_to_goal = (100000 - current) / monthly
            print(f"⏱️  Arvioitu aika tavoitteeseen: {months_to_goal:.1f} kuukautta")
        
        print("\n🤖 SENTINEL AI -AGENTTISI ON VALMIS!")
        print("✅ Reaaliaikainen budjettiseuranta")
        print("✅ Henkilökohtaiset säästövinkit")
        print("✅ Automaattinen kategorisointi")
        print("✅ Tavoitteiden seuranta")
        print("✅ Viikottaiset suositukset")
        
        print(f"\n🚀 KÄYNNISTÄ SENTINEL:")
        print("   python3 sentinel_backend_personal.py")
        print("   Sitten avaa: http://localhost:8000")
        
    def create_personal_backend(self, profile):
        """Create personalized backend with user data"""
        backend_code = f'''#!/usr/bin/env python3

"""
🛡️ SENTINEL 100K - HENKILÖKOHTAINEN BACKEND
==========================================

{profile["user"]["name"]}:n henkilökohtainen rahoitusbackend.
Generoitu automaattisesti onboardingin aikana.

python3 sentinel_backend_personal.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

# User profile (generated from onboarding)
USER_PROFILE = {json.dumps(profile, indent=4, ensure_ascii=False)}

app = FastAPI(
    title="Sentinel 100K - {profile['user']['name']}",
    description="🛡️ Henkilökohtainen rahoitusagentti",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    user = USER_PROFILE["user"]
    financial = USER_PROFILE["financial"]
    
    return {{
        "message": f"🛡️ Sentinel 100K - {{user['name']}}:n agentti",
        "status": "✅ AKTIIVINEN",
        "current_savings": f"{{financial['current_savings']:,.0f}}€",
        "goal_progress": f"{{financial['current_savings']/100000*100:.1f}}%",
        "monthly_savings": f"{{financial['monthly_net']:,.0f}}€",
        "savings_rate": f"{{financial['savings_rate']:.1f}}%"
    }}

@app.get("/health")
async def health():
    return {{
        "status": "healthy",
        "user": USER_PROFILE["user"]["name"],
        "timestamp": datetime.now().isoformat(),
        "onboarding_completed": True
    }}

@app.get("/api/v1/dashboard/summary")
async def dashboard_summary():
    user = USER_PROFILE["user"]
    financial = USER_PROFILE["financial"]
    goals = USER_PROFILE["goals"]
    transactions = USER_PROFILE["transactions"]
    
    main_goal = next((g for g in goals if g["id"] == "main_100k"), goals[0] if goals else None)
    
    return {{
        "user_name": user["name"],
        "current_savings": financial["current_savings"],
        "goal_amount": 100000.0,
        "savings_progress": financial["current_savings"] / 100000 * 100,
        "total_income": financial["monthly_income"],
        "total_expenses": financial["monthly_expenses"]["total"],
        "net_balance": financial["monthly_net"],
        "savings_rate": financial["savings_rate"],
        "transaction_count": len(transactions),
        "recent_transactions": transactions[:5],
        "main_goal": main_goal,
        "last_updated": datetime.now().isoformat()
    }}

@app.get("/api/v1/transactions")
async def get_transactions():
    transactions = USER_PROFILE["transactions"]
    financial = USER_PROFILE["financial"]
    
    return {{
        "transactions": transactions,
        "total_count": len(transactions),
        "income_total": financial["monthly_income"],
        "expense_total": financial["monthly_expenses"]["total"]
    }}

@app.get("/api/v1/goals")
async def get_goals():
    goals = USER_PROFILE["goals"]
    financial = USER_PROFILE["financial"]
    
    return {{
        "goals": goals,
        "main_goal_progress": financial["current_savings"] / 100000 * 100
    }}

@app.post("/api/v1/chat")
async def ai_chat(message: dict):
    user_message = message.get("message", "").lower()
    user = USER_PROFILE["user"]
    financial = USER_PROFILE["financial"]
    
    name = user["name"]
    savings = financial["current_savings"]
    monthly = financial["monthly_net"]
    rate = financial["savings_rate"]
    
    # Personal AI responses
    if "säästä" in user_message or "säästö" in user_message:
        response = f"💰 Hei {{name}}! Sinulla on {{savings:,.0f}}€ säästöjä. Säästät {{monthly:,.0f}}€/kk, mikä on loistavaa!"
    elif "budjetti" in user_message:
        response = f"📊 {{name}}, säästöasteesi on {{rate:.1f}}%. Tavoitellaan yli 20% säästöastetta!"
    elif "tavoite" in user_message:
        remaining = 100000 - savings
        months = remaining / monthly if monthly > 0 else 0
        response = f"🎯 100K€ tavoitteessa sinulla on {{remaining:,.0f}}€ jäljellä. Arviolta {{months:.1f}} kuukautta!"
    elif "moi" in user_message or "hei" in user_message:
        response = f"👋 Hei {{name}}! Olen Sentinel AI -agenttisi. Miten voin auttaa talousiesi kanssa tänään?"
    else:
        response = f"Kiitos {{name}}! Voin auttaa säästämisessä, budjetoinnissa ja 100K€ tavoitteen saavuttamisessa."
    
    return {{
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "user_context": {{
            "name": name,
            "savings": savings,
            "monthly_net": monthly,
            "savings_rate": rate
        }}
    }}

@app.get("/api/v1/profile")
async def get_profile():
    return USER_PROFILE

if __name__ == "__main__":
    print("🛡️ Starting Sentinel 100K - {{USER_PROFILE['user']['name']}}")
    print("=" * 50)
    print(f"👤 Käyttäjä: {{USER_PROFILE['user']['name']}}")
    print(f"💰 Säästöt: {{USER_PROFILE['financial']['current_savings']:,.0f}}€")
    print(f"🎯 Tavoite: 100,000€")
    print(f"📈 Edistyminen: {{USER_PROFILE['financial']['current_savings']/100000*100:.1f}}%")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
    '''
        
        with open("sentinel_backend_personal.py", "w", encoding="utf-8") as f:
            f.write(backend_code)
        
        print(f"🚀 Henkilökohtainen backend luotu: sentinel_backend_personal.py")
    
    def run_onboarding(self):
        """Run the complete onboarding process"""
        self.print_header()
        
        print("🤖 Hei! Olen Sentinel AI, henkilökohtainen rahoitusagenttisi.")
        print("   Autan sinua saavuttamaan 100,000€ säästötavoitteen!\n")
        print("📋 Kerätään ensin perustietosi henkilökohtaista suunnitelmaa varten...")
        
        # Step 1: Personal info
        self.collect_personal_info()
        
        # Step 2: Financial status
        self.collect_financial_status()
        
        # Step 3: Goals
        self.set_goals()
        
        # Step 4: Sample data
        self.create_sample_transactions()
        
        # Step 5: Save profile
        profile = self.save_profile()
        
        # Step 6: Create personal backend
        self.create_personal_backend(profile)
        
        # Step 7: Final summary
        self.show_welcome_summary()

if __name__ == "__main__":
    onboarding = SentinelOnboarding()
    onboarding.run_onboarding() 