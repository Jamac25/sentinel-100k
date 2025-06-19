"""
Guardian API - Aktiivinen 100k€ tavoitteen valvonta ja hälytykset
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..db import get_db
from ..services.sentinel_watchdog_service import SentinelWatchdogService
from ..services.sentinel_learning_engine import SentinelLearningEngine
from ..services.auth_service import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/guardian", tags=["guardian"])

# Palvelujen instanssit
watchdog_service = SentinelWatchdogService()
learning_engine = SentinelLearningEngine()

@router.get("/status", response_model=None)
async def get_watchdog_status(current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Hae Sentinel Watchdog™ tilanneanalyysi ja riskiarvio.
    """
    try:
        status = watchdog_service.analyze_situation_room(current_user.id, db)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virhe tilanneanalyysissä: {str(e)}")

@router.get("/communication", response_model=None)
async def get_watchdog_communication(current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Hae Watchdog-kommunikaatio ja motivaatioviestit.
    """
    try:
        communication = watchdog_service.get_watchdog_communication(current_user.id, db)
        return communication
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virhe kommunikaation haussa: {str(e)}")

@router.get("/suggestions", response_model=None)
async def get_survival_suggestions(current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Hae Goal Survival Engine -ehdotukset.
    """
    try:
        suggestions = watchdog_service.generate_survival_suggestions(current_user.id, db)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virhe ehdotusten haussa: {str(e)}")

@router.get("/emergency-protocol", response_model=None)
async def get_emergency_protocol(current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Hae hätätila-protokolla kun tavoite on kriittisessä vaarassa.
    """
    try:
        protocol = watchdog_service.get_emergency_protocol(current_user.id, db)
        return protocol
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virhe hätäprotokollan haussa: {str(e)}")

@router.get("/health-check", response_model=None)
async def watchdog_health_check():
    """
    Tarkista Sentinel Watchdog™ palvelun toimivuus.
    """
    return {
        "status": "healthy",
        "service": "Sentinel Watchdog™",
        "message": "Valvoo älykkäästi 100k€ tavoitettasi! 🤖🛡️",
        "features": [
            "Tilanneanalyysi (Situation Room)",
            "Toimenpidemoodit (Passiivinen → Hätätila)",
            "Motivoiva kommunikaatio",
            "Goal Survival Engine",
            "Hätätila-protokolla"
        ]
    }

@router.get("/learning/initialize/{user_id}", response_model=None)
async def initialize_learning(user_id, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Alusta oppimismoottori käyttäjälle"""
    try:
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Ei oikeutta")
        
        pattern = learning_engine.initialize_user_learning(user_id, db)
        
        return {
            "status": "success",
            "message": "Oppimismoottori alustettu",
            "communication_style": pattern.communication_style,
            "learning_level": "beginner"
        }
        
    except Exception as e:
        logger.error(f"Virhe oppimisen alustuksessa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning/feedback", response_model=None)
async def submit_learning_feedback(feedback_data, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Lähetä palaute ehdotuksesta oppimista varten"""
    try:
        user_id = current_user.id
        suggestion_id = feedback_data.get("suggestion_id")
        response_type = feedback_data.get("response_type")  # accepted, rejected, ignored, partially_followed
        effectiveness = feedback_data.get("effectiveness")  # 0.0-1.0
        
        if not suggestion_id or not response_type:
            raise HTTPException(status_code=400, detail="Puuttuvia tietoja")
        
        learning_engine.learn_from_user_response(
            user_id, suggestion_id, response_type, effectiveness, db
        )
        
        return {
            "status": "success",
            "message": "Palaute tallennettu, Sentinel oppii!"
        }
        
    except Exception as e:
        logger.error(f"Virhe palautteen tallennuksessa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/predictions/{days_ahead}", response_model=None)
async def get_spending_predictions(days_ahead, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Hae kulutusennusteet ML:llä"""
    try:
        if days_ahead < 1 or days_ahead > 90:
            raise HTTPException(status_code=400, detail="Päivien määrä 1-90")
        
        predictions = learning_engine.predict_spending(current_user.id, days_ahead, db)
        
        return {
            "status": "success",
            "predictions": predictions,
            "user_id": current_user.id,
            "forecast_period": days_ahead
        }
        
    except Exception as e:
        logger.error(f"Virhe ennusteiden haussa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/anomalies", response_model=None)
async def detect_anomalies(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Tunnista epätavalliset kulutuskuviot"""
    try:
        anomalies = learning_engine.detect_spending_anomalies(current_user.id, db)
        
        return {
            "status": "success",
            "anomalies": anomalies,
            "count": len(anomalies),
            "analysis_period": "30 päivää"
        }
        
    except Exception as e:
        logger.error(f"Virhe anomalioiden tunnistuksessa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/suggestions", response_model=None)
async def get_personalized_suggestions(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Hae personoituja ehdotuksia oppimisen perusteella"""
    try:
        suggestions = learning_engine.get_personalized_suggestions(current_user.id, db)
        
        return {
            "status": "success",
            "suggestions": suggestions,
            "personalization_level": "high" if len(suggestions) > 3 else "medium",
            "based_on_learning": True
        }
        
    except Exception as e:
        logger.error(f"Virhe personoitujen ehdotusten haussa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/communication-timing", response_model=None)
async def get_optimal_timing(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Hae optimaalinen kommunikaatioaika"""
    try:
        timing = learning_engine.get_optimal_communication_timing(current_user.id)
        
        return {
            "status": "success",
            "optimal_timing": timing,
            "timezone": "Europe/Helsinki"
        }
        
    except Exception as e:
        logger.error(f"Virhe kommunikaatioajan haussa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/goal-analysis", response_model=None)
async def analyze_goal_progress(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Analysoi tavoitteen edistymistä ja ennusta onnistumista"""
    try:
        analysis = learning_engine.analyze_goal_progress_patterns(current_user.id, db)
        
        return {
            "status": "success",
            "goal_analysis": analysis,
            "target_amount": 100000,
            "currency": "EUR"
        }
        
    except Exception as e:
        logger.error(f"Virhe tavoiteanalyysissä: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/insights", response_model=None)
async def get_learning_insights(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Hae oppimisen tulokset ja oivallukset"""
    try:
        insights = learning_engine.get_learning_insights(current_user.id)
        
        return {
            "status": "success",
            "learning_insights": insights,
            "sentinel_iq": "Kehittyvä" if insights.get('total_interactions', 0) > 10 else "Aloittelija"
        }
        
    except Exception as e:
        logger.error(f"Virhe oppimisen oivallusten haussa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/export", response_model=None)
async def export_learning_data(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Vie käyttäjän oppimisdata"""
    try:
        learning_data = learning_engine.export_learning_data(current_user.id)
        
        return {
            "status": "success",
            "learning_data": learning_data,
            "export_info": "Kaikki oppimisdata viety onnistuneesti"
        }
        
    except Exception as e:
        logger.error(f"Virhe oppimisdatan viennissä: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning/import", response_model=None)
async def import_learning_data(import_data, db=Depends(get_db), current_user=Depends(get_current_user)):
    """Tuo käyttäjän oppimisdata"""
    try:
        # Varmista että data kuuluu käyttäjälle
        if import_data.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Ei oikeutta tuoda toisen käyttäjän dataa")
        
        learning_engine.import_learning_data(import_data)
        
        return {
            "status": "success",
            "message": "Oppimisdata tuotu onnistuneesti",
            "sentinel_status": "Oppiminen jatkuu siitä mihin jäi!"
        }
        
    except Exception as e:
        logger.error(f"Virhe oppimisdatan tuonnissa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning/reset", response_model=None)
async def reset_learning(db=Depends(get_db), current_user=Depends(get_current_user)):
    """Nollaa käyttäjän oppimisdata"""
    try:
        user_id = current_user.id
        
        # Poista oppimisdata
        if user_id in learning_engine.user_patterns:
            del learning_engine.user_patterns[user_id]
        if user_id in learning_engine.learning_history:
            del learning_engine.learning_history[user_id]
        
        # Alusta uudelleen
        learning_engine.initialize_user_learning(user_id, db)
        
        return {
            "status": "success",
            "message": "Oppimisdata nollattu, Sentinel aloittaa alusta!",
            "new_learning_level": "beginner"
        }
        
    except Exception as e:
        logger.error(f"Virhe oppimisen nollauksessa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/health-check", response_model=None)
async def learning_health_check():
    """Tarkista oppimismoottorin tila"""
    try:
        active_users = len(learning_engine.user_patterns)
        total_interactions = sum(len(history) for history in learning_engine.learning_history.values())
        
        return {
            "status": "healthy",
            "active_learning_users": active_users,
            "total_learning_interactions": total_interactions,
            "ml_models_loaded": True,
            "learning_engine_version": "1.0.0",
            "capabilities": [
                "Spending Prediction",
                "Anomaly Detection", 
                "Personalized Suggestions",
                "Communication Optimization",
                "Goal Progress Analysis",
                "Behavioral Pattern Learning"
            ]
        }
        
    except Exception as e:
        logger.error(f"Virhe oppimismoottorin terveystarkistuksessa: {e}")
        return {
            "status": "error",
            "error": str(e)
        } 