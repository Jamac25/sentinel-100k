#!/usr/bin/env python3
"""
Sentinel 100K - OpenAI API
Käyttää oikeaa OpenAI GPT-3.5-turbo mallia
"""
from fastapi import FastAPI
from app.core.config import settings
from app.services.openai_service import openai_service

app = FastAPI(title="Sentinel 100K - OpenAI API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "🎯 Sentinel 100K - OpenAI Powered",
        "model": "GPT-3.5-turbo",
        "openai_configured": bool(settings.openai_api_key),
        "llm_service": settings.llm_service,
        "status": "ready"
    }

@app.get("/health")
async def health():
    """Terveystarkistus OpenAI:lle"""
    return openai_service.health_check()

@app.get("/stats")
async def stats():
    """OpenAI-palvelun tilastot"""
    return openai_service.get_stats()

@app.post("/advice")
async def get_financial_advice(user_data: dict):
    """Hae talousneuvoja OpenAI:lta"""
    advice = openai_service.generate_financial_advice(user_data)
    return {
        "advice": advice,
        "source": "OpenAI GPT-3.5-turbo",
        "personalized": True
    }

@app.post("/motivation")
async def get_motivation(progress_data: dict):
    """Hae motivaatioviestiä OpenAI:lta"""
    motivation = openai_service.generate_motivation_message(progress_data)
    return {
        "motivation": motivation,
        "source": "OpenAI GPT-3.5-turbo",
        "personalized": True
    }

@app.get("/test-ai")
async def test_ai():
    """Testaa OpenAI-toiminnallisuutta"""
    # Testaa talousneuvoja
    advice = openai_service.generate_financial_advice({
        'category': 'ruoka', 
        'current_spending': 400,
        'suggested_reduction': 100,
        'over_budget_percent': 25
    })
    
    # Testaa motivaatiota
    motivation = openai_service.generate_motivation_message({
        'monthly_savings': 800,
        'current_month_savings': 650,
        'streak_days': 14,
        'total_progress': 15,
        'mood': 'good'
    })
    
    return {
        "ai_working": True,
        "openai_model": "gpt-3.5-turbo",
        "financial_advice": advice,
        "motivation": motivation,
        "cost_estimate": openai_service.get_stats()["cost_estimate"],
        "requests_made": openai_service.request_count
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Käynnistetään Sentinel 100K OpenAI API...")
    print(f"💰 OpenAI API-avain: {'✅ Asetettu' if settings.openai_api_key else '❌ Puuttuu'}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
