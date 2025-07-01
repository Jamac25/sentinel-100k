#!/usr/bin/env python3

"""
🛡️ MUKTAR:IN SENTINEL 100K - LOPULLINEN BACKEND
=============================================

Muktar:in henkilökohtainen rahoitusagentti päivitetyillä luvuilla.
Sisältää 500€/kk tuen lapsille Somaliaan.

python3 muktar_final_backend.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

# Muktar:in päivitetty profiili (sis. 500€ perhetuki)
MUKTAR_DATA = {
    "user_name": "Muktar",
    "current_savings": 220.0,
    "goal_amount": 100000.0,
    "monthly_income": 4700.0,
    "monthly_expenses": 3070.0,  # päivitetty +500€ perhetuki
    "monthly_savings": 1630.0,   # 4700 - 3070
    "savings_rate": 34.7,        # (1630/4700)*100
    "months_to_goal": 61,        # (100000-220)/1630
    "transactions": [
        {
            "id": "income_1",
            "amount": 3200.0,
            "description": "Palkka - Terveystalo",
            "category": "palkka",
            "type": "income",
            "date": "2024-11-08T12:00:00Z",
            "merchant": "Terveystalo"
        },
        {
            "id": "income_2", 
            "amount": 1500.0,
            "description": "Oma yritystoiminta",
            "category": "yritys",
            "type": "income",
            "date": "2024-11-10T14:00:00Z",
            "merchant": "Oma yritys"
        },
        {
            "id": "expense_1",
            "amount": -1500.0,
            "description": "Vuokra",
            "category": "asuminen",
            "type": "expense",
            "date": "2024-11-12T10:00:00Z",
            "merchant": "Vuokranantaja"
        },
        {
            "id": "expense_2",
            "amount": -500.0,
            "description": "Tuki lapsille Somaliaan",
            "category": "perhe",
            "type": "expense", 
            "date": "2024-11-05T16:00:00Z",
            "merchant": "Perhetuki Somalia"
        },
        {
            "id": "expense_3",
            "amount": -89.50,
            "description": "Ruokaostokset K-Market",
            "category": "ruoka",
            "type": "expense",
            "date": "2024-11-11T18:30:00Z",
            "merchant": "K-Market"
        },
        {
            "id": "expense_4",
            "amount": -65.0,
            "description": "Bussikortti",
            "category": "liikenne", 
            "type": "expense",
            "date": "2024-11-03T09:00:00Z",
            "merchant": "HSL"
        }
    ]
}

app = FastAPI(
    title="Sentinel 100K - Muktar (Final)",
    description="🛡️ Muktar:in henkilökohtainen rahoitusagentti - päivitetty versio",
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
    return {
        "message": "🛡️ Sentinel 100K - Muktar:in henkilökohtainen agentti",
        "status": "✅ PÄIVITETTY - Perhetuki mukana",
        "current_savings": f"{MUKTAR_DATA['current_savings']:,.0f}€",
        "monthly_savings": f"{MUKTAR_DATA['monthly_savings']:,.0f}€",
        "savings_rate": f"{MUKTAR_DATA['savings_rate']:.1f}%",
        "months_to_goal": f"{MUKTAR_DATA['months_to_goal']:.1f} kuukautta",
        "family_support": "500€/kk lapsille Somaliaan ❤️"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "user": "Muktar",
        "timestamp": datetime.now().isoformat(),
        "family_support_included": True,
        "backend_version": "final"
    }

@app.get("/api/v1/dashboard/summary")
async def dashboard_summary():
    return {
        "user_name": MUKTAR_DATA["user_name"],
        "current_savings": MUKTAR_DATA["current_savings"],
        "goal_amount": MUKTAR_DATA["goal_amount"],
        "savings_progress": MUKTAR_DATA["current_savings"] / MUKTAR_DATA["goal_amount"] * 100,
        "total_income": MUKTAR_DATA["monthly_income"],
        "total_expenses": MUKTAR_DATA["monthly_expenses"],
        "net_balance": MUKTAR_DATA["monthly_savings"],
        "savings_rate": MUKTAR_DATA["savings_rate"],
        "months_to_goal": MUKTAR_DATA["months_to_goal"],
        "transaction_count": len(MUKTAR_DATA["transactions"]),
        "recent_transactions": MUKTAR_DATA["transactions"][:5],
        "family_support": {
            "amount": 500.0,
            "description": "Tuki lapsille Somaliaan",
            "included_in_budget": True
        },
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/transactions")
async def get_transactions():
    return {
        "transactions": MUKTAR_DATA["transactions"],
        "total_count": len(MUKTAR_DATA["transactions"]),
        "income_total": MUKTAR_DATA["monthly_income"],
        "expense_total": MUKTAR_DATA["monthly_expenses"],
        "family_support_included": True
    }

@app.get("/api/v1/goals")
async def get_goals():
    return {
        "goals": [
            {
                "id": "main_100k",
                "name": "Hätävara 100K€",
                "target_amount": MUKTAR_DATA["goal_amount"],
                "current_amount": MUKTAR_DATA["current_savings"],
                "progress_percent": MUKTAR_DATA["current_savings"] / MUKTAR_DATA["goal_amount"] * 100,
                "monthly_target": MUKTAR_DATA["monthly_savings"],
                "estimated_months": MUKTAR_DATA["months_to_goal"],
                "status": "active"
            }
        ],
        "estimated_completion": {
            "months": MUKTAR_DATA["months_to_goal"],
            "years": MUKTAR_DATA["months_to_goal"] / 12
        }
    }

@app.post("/api/v1/chat")
async def ai_chat(message: dict):
    user_message = message.get("message", "").lower()
    
    # Muktar:in henkilökohtaiset AI-vastaukset
    if "säästä" in user_message or "säästö" in user_message:
        response = f"💰 Hei Muktar! Säästät {MUKTAR_DATA['monthly_savings']:,.0f}€/kk. Säästöasteesi {MUKTAR_DATA['savings_rate']:.1f}% on erinomainen, vaikka tuet perhettäsi Somaliassa!"
    elif "perhe" in user_message or "lapsi" in user_message or "somalia" in user_message:
        response = "❤️ Perheen tukeminen on tärkeää! 500€/kk lapsillesi Somaliaan on arvokasta. Säästöasteesi 34.7% on edelleen loistava."
    elif "tavoite" in user_message or "100k" in user_message:
        response = f"🎯 100K€ tavoitteessa sinulla on {MUKTAR_DATA['goal_amount'] - MUKTAR_DATA['current_savings']:,.0f}€ jäljellä. Saavutat tavoitteen {MUKTAR_DATA['months_to_goal']:.1f} kuukaudessa!"
    elif "terveystalo" in user_message or "yritys" in user_message:
        response = "💼 Terveystalon palkka 3200€ + oma yritys 1500€ = loistavat tulot! Monipuoliset tulonlähteet antavat turvaa."
    elif "budjetti" in user_message:
        response = f"📊 Muktar, budjettisi on loistava! {MUKTAR_DATA['savings_rate']:.1f}% säästöaste on huippuluokkaa, perhetuki mukaan lukien."
    elif "moi" in user_message or "hei" in user_message:
        response = f"👋 Hei Muktar! Säästöasteesi {MUKTAR_DATA['savings_rate']:.1f}% on huippuluokkaa. Perheesi tuki Somaliassa on arvokasta!"
    else:
        response = f"Kiitos Muktar! Säästöasteesi {MUKTAR_DATA['savings_rate']:.1f}% on erinomainen. Voin auttaa 100K€ tavoitteessa."
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "user_context": {
            "name": "Muktar",
            "savings": MUKTAR_DATA["current_savings"],
            "monthly_savings": MUKTAR_DATA["monthly_savings"],
            "savings_rate": MUKTAR_DATA["savings_rate"],
            "family_support": 500.0
        }
    }

@app.get("/api/v1/profile")
async def get_profile():
    return {
        "user": {
            "name": "Muktar",
            "onboarding_completed": True
        },
        "financial": {
            "current_savings": MUKTAR_DATA["current_savings"],
            "monthly_income": MUKTAR_DATA["monthly_income"],
            "monthly_expenses": MUKTAR_DATA["monthly_expenses"],
            "monthly_savings": MUKTAR_DATA["monthly_savings"],
            "savings_rate": MUKTAR_DATA["savings_rate"],
            "family_support": 500.0
        },
        "goals": [
            {
                "name": "Hätävara 100K€",
                "target": MUKTAR_DATA["goal_amount"],
                "current": MUKTAR_DATA["current_savings"],
                "months_remaining": MUKTAR_DATA["months_to_goal"]
            }
        ]
    }

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
            {"id": "perhe", "name": "Perhetuki", "type": "expense", "color": "#F97316"}
        ]
    }

if __name__ == "__main__":
    print("🛡️ Muktar:in Sentinel 100K - LOPULLINEN VERSIO")
    print("=" * 55)
    print(f"👤 Käyttäjä: Muktar")
    print(f"💰 Säästöt: {MUKTAR_DATA['current_savings']:,.0f}€")
    print(f"📈 Kuukausisäästö: {MUKTAR_DATA['monthly_savings']:,.0f}€")
    print(f"🎯 Säästöaste: {MUKTAR_DATA['savings_rate']:.1f}%")
    print(f"❤️ Perhetuki: 500€/kk (Somalia)")
    print(f"⏰ Tavoite: {MUKTAR_DATA['months_to_goal']:.1f} kuukaudessa")
    print("=" * 55)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    ) 