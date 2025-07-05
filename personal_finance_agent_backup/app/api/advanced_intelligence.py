from fastapi import APIRouter, Depends, HTTPException
from ..db import get_db
from ..services.income_stream_intelligence import IncomeStreamIntelligence
from ..services.liabilities_insight import LiabilitiesInsight
from ..services.idea_engine import IdeaEngine
from ..services.auth_service import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligence", tags=["advanced_intelligence"])

# Palvelujen instanssit
income_intelligence = IncomeStreamIntelligence()
liabilities_insight = LiabilitiesInsight()
idea_engine = IdeaEngine()

# Income Stream Intelligence
@router.get("/income/analysis", response_model=None)
async def analyze_income_streams(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Analysoi tulovirrat ja ehdottaa optimointia"""
    try:
        analysis = income_intelligence.analyze_income_streams(current_user.id, db)
        return {"status": "success", "income_analysis": analysis}
    except Exception as e:
        logger.error(f"Virhe tuloanalyysissä: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/income/daily-opportunity", response_model=None)
async def get_daily_income_opportunity(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Hae päivittäinen tulonlisäysmahdollisuus"""
    try:
        opportunity = income_intelligence.get_daily_income_opportunity(current_user.id)
        return {"status": "success", "daily_opportunity": opportunity}
    except Exception as e:
        logger.error(f"Virhe päivittäisen mahdollisuuden haussa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Liabilities Insight
@router.get("/liabilities/analysis", response_model=None)
async def analyze_liabilities(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Analysoi velat ja luo optimointisuunnitelman"""
    try:
        analysis = liabilities_insight.analyze_liabilities(current_user.id, db)
        return {"status": "success", "liabilities_analysis": analysis}
    except Exception as e:
        logger.error(f"Virhe velka-analyysissä: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/liabilities/calculate-payoff", response_model=None)
async def calculate_debt_payoff(liability_data, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Laske velan maksusuunnitelma"""
    try:
        extra_payment = liability_data.get("extra_payment", 0)
        result = liabilities_insight.get_debt_payoff_calculator(liability_data, extra_payment)
        return {"status": "success", "payoff_calculation": result}
    except Exception as e:
        logger.error(f"Virhe maksusuunnitelman laskennassa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Idea Engine
@router.get("/ideas/daily", response_model=None)
async def get_daily_ideas(user_profile=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Hae päivittäiset ansaintaideat"""
    try:
        ideas = idea_engine.get_daily_ideas(current_user.id, user_profile)
        return {"status": "success", "daily_ideas": ideas}
    except Exception as e:
        logger.error(f"Virhe päivittäisten ideoiden haussa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ideas/action-plan", response_model=None)
async def create_action_plan(selected_ideas, user_schedule=None, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Luo toimintasuunnitelma valituille ideoille"""
    try:
        plan = idea_engine.create_action_plan(selected_ideas, user_schedule)
        return {"status": "success", "action_plan": plan}
    except Exception as e:
        logger.error(f"Virhe toimintasuunnitelman luonnissa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ideas/track-performance", response_model=None)
async def track_idea_performance(idea_id, performance_result, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Seuraa idean suorituskykyä"""
    try:
        result = idea_engine.track_idea_performance(current_user.id, idea_id, performance_result)
        return {"status": "success", "performance_tracked": result}
    except Exception as e:
        logger.error(f"Virhe suorituskyvyn seurannassa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Combined Intelligence Dashboard
@router.get("/dashboard/comprehensive", response_model=None)
async def get_comprehensive_intelligence_dashboard(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Hae kattava älykkyyden dashboard"""
    try:
        # Hae kaikki analyysit
        income_analysis = income_intelligence.analyze_income_streams(current_user.id, db)
        liabilities_analysis = liabilities_insight.analyze_liabilities(current_user.id, db)
        daily_ideas = idea_engine.get_daily_ideas(current_user.id)
        
        # Yhdistä tulokset
        dashboard = {
            "status": "success",
            "income_intelligence": income_analysis,
            "liabilities_insight": liabilities_analysis,
            "idea_engine": daily_ideas,
            "financial_health_score": calculate_financial_health_score(income_analysis, liabilities_analysis),
            "recommendations": generate_comprehensive_recommendations(income_analysis, liabilities_analysis, daily_ideas)
        }
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Virhe kattavan dashboardin haussa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_financial_health_score(income_analysis, liabilities_analysis):
    """Laske kokonaisvaltainen taloudellinen terveyspistemäärä"""
    try:
        score = 0.0
        
        # Tulojen terveys (40%)
        if income_analysis.get("status") == "success":
            income_health = income_analysis.get("analysis", {}).get("health_score", 0)
            score += income_health * 0.4
        
        # Velkojen terveys (35%)
        if liabilities_analysis.get("status") == "success":
            debt_analysis = liabilities_analysis.get("debt_analysis", {})
            debt_status = debt_analysis.get("debt_status", "manageable")
            debt_scores = {"manageable": 1.0, "moderate": 0.7, "concerning": 0.4, "critical": 0.1}
            debt_score = debt_scores.get(debt_status, 0.5)
            score += debt_score * 0.35
        
        # Diversifikaatio (25%)
        income_streams = income_analysis.get("total_streams", 0)
        diversity_score = min(1.0, income_streams / 3)  # Parempi jos useita tulolähteitä
        score += diversity_score * 0.25
        
        return min(1.0, max(0.0, score))
        
    except Exception as e:
        logger.error(f"Virhe terveyspistemäärän laskennassa: {e}")
        return 0.5

def generate_comprehensive_recommendations(income_analysis, liabilities_analysis, idea_engine):
    """Generoi kattavat suositukset"""
    recommendations = []
    
    # Tulojen suositukset
    if income_analysis.get("status") == "success":
        income_health = income_analysis.get("analysis", {}).get("health_score", 0)
        if income_health < 0.5:
            recommendations.append("🚨 Tulojesi vakaus vaatii huomiota - diversifioi tulolähteitäsi")
        elif income_health < 0.7:
            recommendations.append("⚠️ Tulojesi vakaus on kohtalainen - harkitse lisätuloja")
    
    # Velkojen suositukset
    if liabilities_analysis.get("status") == "success":
        debt_status = liabilities_analysis.get("debt_analysis", {}).get("debt_status", "manageable")
        if debt_status in ["concerning", "critical"]:
            recommendations.append("💳 Velkatilanne vaatii välitöntä huomiota - priorisoi velkojen maksaminen")
    
    # Ideoiden suositukset
    if idea_engine.get("status") == "success":
        total_potential = idea_engine.get("total_potential_earning", 0)
        if total_potential > 200:
            recommendations.append(f"💡 Tänään on {total_potential:.0f}€ ansaintaipotentiaali - hyödynnä se!")
    
    # Yleiset suositukset
    recommendations.append("📊 Seuraa taloudellista terveyttäsi säännöllisesti")
    recommendations.append("🎯 Keskity ensin kriittisimpiin parannuksiin")
    
    return recommendations[:5]  # Maksimissaan 5 suositusta 