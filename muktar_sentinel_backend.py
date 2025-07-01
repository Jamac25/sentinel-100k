#!/usr/bin/env python3

"""
🛡️ SENTINEL 100K - MUKTAR:IN HENKILÖKOHTAINEN BACKEND
==================================================

Muktar:in henkilökohtainen rahoitusagentti.
Generoitu onboardingin perusteella 13.11.2024

python3 muktar_sentinel_backend.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
from typing import Dict, Any

# Muktar:in henkilökohtainen profiili
MUKTAR_PROFILE = {
    "user": {
        "name": "Muktar",
        "created_at": datetime.now().isoformat(),
        "onboarding_completed": True
    },
    "financial": {
        "current_savings": 220.0,
        "monthly_income": 4700.0,
        "monthly_expenses": {
            "housing": 1720.0,  # vuokra 1500 + sähkö 50 + netti 20 + muut 150
            "food": 500.0,
            "transport": 200.0,
            "entertainment": 100.0,
            "clothing": 50.0,
            "family_support": 500.0,  # lapsille Somaliaan
            "total": 3070.0
        },
        "monthly_net": 1630.0,  # 4700 - 3070
        "savings_rate": 34.7  # (1630/4700)*100
    },
    "goals": [
        {
            "id": "main_100k",
            "name": "Hätävara 100K€",
            "description": "Tavoitteena on saavuttaa 100,000€ säästöt taloudellista turvaa varten",
            "target_amount": 100000.0,
            "current_amount": 220.0,
            "progress_percent": 0.22,  # 220/100000*100
            "monthly_target": 1630.0,
            "estimated_months": 61,  # (100000-220)/1630
            "status": "active"
        }
    ],
    "transactions": [
        # Muktar:in tyypilliset kuukauden tapahtumat
        {
            "id": "income_terveystalo",
            "amount": 3200.0,
            "description": "Palkka - Terveystalo",
            "category": "palkka",
            "category_name": "Palkka",
            "type": "income",
            "date": (datetime.now() - timedelta(days=5)).isoformat(),
            "merchant": "Terveystalo"
        },
        {
            "id": "income_business",
            "amount": 1500.0,
            "description": "Oma yritystoiminta",
            "category": "yritys",
            "category_name": "Yritystulot",
            "type": "income",
            "date": (datetime.now() - timedelta(days=3)).isoformat(),
            "merchant": "Oma yritys"
        },
        {
            "id": "expense_rent",
            "amount": -1500.0,
            "description": "Vuokra",
            "category": "asuminen",
            "category_name": "Asuminen",
            "type": "expense",
            "date": (datetime.now() - timedelta(days=1)).isoformat(),
            "merchant": "Vuokranantaja"
        },
        {
            "id": "expense_electricity",
            "amount": -50.0,
            "description": "Sähkölasku",
            "category": "asuminen",
            "category_name": "Asuminen",
            "type": "expense",
            "date": (datetime.now() - timedelta(days=7)).isoformat(),
            "merchant": "Sähköyhtiö"
        },
        {
            "id": "expense_food1",
            "amount": -89.50,
            "description": "Ruokaostokset",
            "category": "ruoka",
            "category_name": "Ruoka",
            "type": "expense",
            "date": (datetime.now() - timedelta(days=2)).isoformat(),
            "merchant": "K-Market"
        },
        {
            "id": "expense_food2",
            "amount": -125.80,
            "description": "Ruokaostokset",
            "category": "ruoka",
            "category_name": "Ruoka",
            "type": "expense",
            "date": (datetime.now() - timedelta(days=6)).isoformat(),
            "merchant": "Prisma"
        },
        {
            "id": "expense_transport",
            "amount": -65.0,
            "description": "Bussikortti",
            "category": "liikenne",
            "category_name": "Liikenne",
            "type": "expense",
            "date": (datetime.now() - timedelta(days=10)).isoformat(),
            "merchant": "HSL"
        },
                 {
             "id": "expense_entertainment",
             "amount": -12.90,
             "description": "Netflix tilaus",
             "category": "viihde",
             "category_name": "Viihde",
             "type": "expense",
             "date": (datetime.now() - timedelta(days=4)).isoformat(),
             "merchant": "Netflix"
         },
         {
             "id": "expense_family_support",
             "amount": -500.0,
             "description": "Tuki lapsille Somaliaan",
             "category": "perhe",
             "category_name": "Perhetuki",
             "type": "expense",
             "date": (datetime.now() - timedelta(days=8)).isoformat(),
             "merchant": "Perhetuki Somalia"
         }
    ]
}

app = FastAPI(
    title="Sentinel 100K - Muktar",
    description="🛡️ Muktar:in henkilökohtainen rahoitusagentti",
    version="1.0.0"
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
    financial = MUKTAR_PROFILE["financial"]
    
    return {
        "message": "🛡️ Sentinel 100K - Muktar:in henkilökohtainen agentti",
        "status": "✅ AKTIIVINEN",
        "current_savings": f"{financial['current_savings']:,.0f}€",
        "goal_progress": f"{financial['current_savings']/100000*100:.2f}%",
        "monthly_savings": f"{financial['monthly_net']:,.0f}€",
        "savings_rate": f"{financial['savings_rate']:.1f}%",
        "months_to_goal": f"{(100000-financial['current_savings'])/financial['monthly_net']:.1f} kuukautta"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "user": "Muktar",
        "timestamp": datetime.now().isoformat(),
        "onboarding_completed": True,
        "backend_type": "personalized"
    }

@app.get("/api/v1/dashboard/summary")
async def dashboard_summary():
    financial = MUKTAR_PROFILE["financial"]
    goals = MUKTAR_PROFILE["goals"]
    transactions = MUKTAR_PROFILE["transactions"]
    
    main_goal = goals[0]
    
    return {
        "user_name": "Muktar",
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
        "months_to_goal": (100000 - financial["current_savings"]) / financial["monthly_net"],
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/transactions")
async def get_transactions():
    transactions = MUKTAR_PROFILE["transactions"]
    financial = MUKTAR_PROFILE["financial"]
    
    return {
        "transactions": transactions,
        "total_count": len(transactions),
        "income_total": financial["monthly_income"],
        "expense_total": financial["monthly_expenses"]["total"]
    }

@app.get("/api/v1/goals")
async def get_goals():
    goals = MUKTAR_PROFILE["goals"]
    financial = MUKTAR_PROFILE["financial"]
    
    return {
        "goals": goals,
        "main_goal_progress": financial["current_savings"] / 100000 * 100,
        "estimated_completion": {
            "months": (100000 - financial["current_savings"]) / financial["monthly_net"],
            "years": ((100000 - financial["current_savings"]) / financial["monthly_net"]) / 12
        }
    }

@app.post("/api/v1/chat")
async def ai_chat(message: dict):
    user_message = message.get("message", "").lower()
    financial = MUKTAR_PROFILE["financial"]
    
    savings = financial["current_savings"]
    monthly = financial["monthly_net"]
    rate = financial["savings_rate"]
    months_to_goal = (100000 - savings) / monthly
    
         # Muktar:in henkilökohtaiset AI-vastaukset
     if "säästä" in user_message or "säästö" in user_message:
         response = f"💰 Hei Muktar! Sinulla on {savings:,.0f}€ säästöjä ja säästät {monthly:,.0f}€/kk. Säästöasteesi {rate:.1f}% on erinomainen, vaikka tuet perhettäsi Somaliassa!"
    elif "budjetti" in user_message:
        response = f"📊 Muktar, budjettisi on loistava! {rate:.1f}% säästöaste on huippuluokkaa. Jatka samaan malliin!"
    elif "tavoite" in user_message or "100k" in user_message:
        remaining = 100000 - savings
        response = f"🎯 100K€ tavoitteessa sinulla on {remaining:,.0f}€ jäljellä. Nykyisellä {monthly:,.0f}€/kk säästöllä saavutat tavoitteen {months_to_goal:.1f} kuukaudessa!"
    elif "terveystalo" in user_message or "työ" in user_message:
        response = "💼 Terveystalon palkka 3200€ + oma yritys 1500€ = loistavat tulot! Monipuoliset tulonlähteet ovat erinomaista riskienhallintaa."
         elif "yritys" in user_message:
         response = "🚀 Oma yritystoiminta tuo 1500€/kk - mahtavaa! Voisitko kasvattaa yritystuloja entisestään nopeuttaaksesi 100K€ tavoitetta?"
     elif "perhe" in user_message or "lapsi" in user_message or "somalia" in user_message:
         response = "❤️ Perheen tukeminen on tärkeää! 500€/kk lapsillesi Somaliaan on arvokasta. Säästöasteesi 34.7% on edelleen loistava."
    elif "moi" in user_message or "hei" in user_message:
        response = f"👋 Hei Muktar! Olen Sentinel AI -agenttisi. Sinulla menee taloudellisesti loistavasti - {rate:.1f}% säästöaste on huippuluokkaa!"
    elif "kuinka kauan" in user_message or "milloin" in user_message:
        response = f"⏰ Nykyisellä säästövauhdilla saavutat 100K€ tavoitteen {months_to_goal:.1f} kuukaudessa (noin {months_to_goal/12:.1f} vuodessa)!"
    elif "vinkkejä" in user_message or "neuvoja" in user_message:
        response = "💡 Vinkki: Säästöasteesi on jo loistava! Voisit harkita sijoittamista indeksirahastoihin nopeuttaaksesi varallisuuden kasvua."
    else:
        response = f"Kiitos Muktar! Voin auttaa säästämisessä ja 100K€ tavoitteessa. Säästöasteesi {rate:.1f}% on erinomainen!"
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "user_context": {
            "name": "Muktar",
            "savings": savings,
            "monthly_net": monthly,
            "savings_rate": rate,
            "months_to_goal": months_to_goal
        }
    }

@app.get("/api/v1/profile")
async def get_profile():
    return MUKTAR_PROFILE

@app.get("/api/v1/categories")
async def get_categories():
    return {
        "categories": [
            {"id": "palkka", "name": "Palkka", "type": "income", "color": "#10B981"},
            {"id": "yritys", "name": "Yritystulot", "type": "income", "color": "#059669"},
            {"id": "asuminen", "name": "Asuminen", "type": "expense", "color": "#3B82F6"},
            {"id": "ruoka", "name": "Ruoka", "type": "expense", "color": "#EF4444"},
            {"id": "liikenne", "name": "Liikenne", "type": "expense", "color": "#F59E0B"},
            {"id": "viihde", "name": "Viihde", "type": "expense", "color": "#8B5CF6"},
                         {"id": "vaatteet", "name": "Vaatteet", "type": "expense", "color": "#EC4899"},
             {"id": "perhe", "name": "Perhetuki", "type": "expense", "color": "#F97316"}
        ]
    }

# Muktar:in henkilökohtaiset finanssimetriikat
@app.get("/api/v1/metrics")
async def get_personal_metrics():
    financial = MUKTAR_PROFILE["financial"]
    
    return {
        "savings_rate": financial["savings_rate"],
        "months_to_100k": (100000 - financial["current_savings"]) / financial["monthly_net"],
        "years_to_100k": ((100000 - financial["current_savings"]) / financial["monthly_net"]) / 12,
        "daily_savings": financial["monthly_net"] / 30,
        "weekly_savings": financial["monthly_net"] / 4.33,
        "current_runway": financial["current_savings"] / financial["monthly_expenses"]["total"],
        "income_sources": {
            "terveystalo": 3200,
            "oma_yritys": 1500,
            "diversification_score": "Excellent"
        }
    }

if __name__ == "__main__":
    print("🛡️ Starting Sentinel 100K - Muktar:in henkilökohtainen agentti")
    print("=" * 60)
    print(f"👤 Käyttäjä: Muktar")
    print(f"💰 Nykyiset säästöt: {MUKTAR_PROFILE['financial']['current_savings']:,.0f}€")
    print(f"📈 Kuukausisäästö: {MUKTAR_PROFILE['financial']['monthly_net']:,.0f}€")
    print(f"🎯 Säästöaste: {MUKTAR_PROFILE['financial']['savings_rate']:.1f}%")
    print(f"⏰ Tavoite: {(100000-MUKTAR_PROFILE['financial']['current_savings'])/MUKTAR_PROFILE['financial']['monthly_net']:.1f} kuukaudessa")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    ) 