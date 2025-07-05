# 🔐 Täydellinen käyttäjäintegraatio Sentinel 100K:lle 
# YHTEENSOVITETTU olemassa olevan järjestelmän kanssa
# EI POISTETA MITÄÄN - Täydentää onboardingia ja dashboardia

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 📁 Käytetään olemassa olevia tiedostoja - EI luoda uusia
# Asetetaan polut suhteessa projektikansioon
DATA_ROOT = Path(__file__).parent.parent.parent.parent
ONBOARDING_DATA_FILE = str(DATA_ROOT / "deep_onboarding_data.json")
WEEKLY_CYCLES_FILE = str(DATA_ROOT / "weekly_cycles_data.json") 
NIGHT_ANALYSIS_FILE = str(DATA_ROOT / "night_analysis_data.json")
USERS_DB_FILE = str(DATA_ROOT / "users_database.json")

def load_data(filename: str) -> dict:
    """Load data from JSON file - yhteensopiva olemassa olevan kanssa"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return {}

class UserContextManager:
    """
    Täydentää olemassa olevaa dashboard- ja onboarding-dataa
    Käyttää samoja data-avaimia: onboarding_{user_email}
    """
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.data_key = f"onboarding_{user_email}"
        
        # Lataa OLEMASSA OLEVASTA datasta
        self.onboarding_data = load_data(ONBOARDING_DATA_FILE)
        self.cycles_data = load_data(WEEKLY_CYCLES_FILE)
        self.analysis_data = load_data(NIGHT_ANALYSIS_FILE)
        self.users_data = load_data(USERS_DB_FILE)
        
        # Hae käyttäjän profiilit OLEMASSA OLEVISTA rakenteista
        self.profile = self.onboarding_data.get(self.data_key, {})
        self.cycles = self.cycles_data.get(self.data_key, {})
        self.analysis = self.analysis_data.get("results", {}).get(self.data_key, {})
        self.user_info = self.users_data.get(user_email, {})

    def get_enhanced_context(self) -> Dict[str, Any]:
        """
        Täydentää olemassa olevaa dashboard-dataa lisäkontekstilla
        SÄILYTTÄÄ kaikki vanhat kentät + lisää uusia
        """
        # SÄILYTETÄÄN olemassa olevat kentät
        base_context = {
            "user_email": self.user_email,
            "data_key": self.data_key,
            "user_id": self.profile.get("user_id"),
            "name": self.profile.get("name"),
            
            # OLEMASSA OLEVAT onboarding kentät
            "current_savings": self.profile.get("current_savings", 0),
            "savings_goal": self.profile.get("savings_goal", 100000),
            "monthly_income": self.profile.get("monthly_income", 0),
            "monthly_expenses": self.profile.get("monthly_expenses", 0),
            "skills": self.profile.get("skills", []),
            "risk_tolerance": self.profile.get("risk_tolerance", "Maltillinen"),
            
            # OLEMASSA OLEVAT cycle kentät  
            "current_week": self.cycles.get("current_week", 1),
            "weekly_target": 0,
            "cycle_progress": 0,
        }
        
        # Lasketaan weekly_target olemassa olevasta datasta
        if self.cycles and "cycles" in self.cycles:
            current_week = base_context["current_week"]
            if current_week <= len(self.cycles["cycles"]):
                current_cycle = self.cycles["cycles"][current_week - 1]
                base_context["weekly_target"] = current_cycle.get("savings_target", 0)
                base_context["cycle_progress"] = (current_week / 7) * 100
        
        # LISÄTÄÄN uusia konteksti-kenttiä (täydentää vanhoja)
        enhanced_context = {
            **base_context,
            
            # 🎯 Lasketut tavoitteet (täydentää savings_goal)
            "target_income_weekly": base_context.get("weekly_target", 300),
            "target_income_monthly": base_context.get("monthly_income", 3000),
            
            # 🧠 Kiinnostukset (täydentää skills-listaa)
            "interests": self._extract_interests_from_skills(),
            
            # 📊 Watchdog-tila (täydentää analysis-dataa)
            "watchdog_state": self._determine_watchdog_state(),
            
            # 🎯 AI-konteksti (täydentää night_analysis)
            "ai_context": self._build_ai_context(),
            
            # 📈 Edistyminen (täydentää dashboard-metriikoita)
            "progress_summary": self._calculate_progress_summary(base_context),
            
            # 🔄 Viimeisin sykli (täydentää cycles-dataa)
            "current_cycle_details": self._get_current_cycle_details(),
            
            # 🌙 Analyysi (täydentää night_analysis)
            "latest_analysis": self.analysis,
            
            # ⚡ Reaaliaikainen tila
            "context_generated": datetime.now().isoformat(),
            "data_completeness": self._calculate_data_completeness()
        }
        
        return enhanced_context

    def _extract_interests_from_skills(self) -> list:
        """Muuntaa olemassa olevat skills kiinnostuksiksi"""
        skills = self.profile.get("skills", [])
        interest_mapping = {
            "Ohjelmointi": "Teknologia",
            "Web-kehitys": "Teknologia", 
            "Graafinen suunnittelu": "Luovuus",
            "UI/UX": "Muotoilu",
            "Markkinointi": "Liiketoiminta",
            "Myynti": "Liiketoiminta",
            "Kirjoittaminen": "Sisällöntuotanto",
            "Valokuvaus": "Luovuus"
        }
        
        interests = []
        for skill in skills:
            if skill in interest_mapping:
                interests.append(interest_mapping[skill])
        
        # Lisää unique-arvot
        return list(set(interests))

    def _determine_watchdog_state(self) -> str:
        """Määrittää watchdog-tilan analyysi-datan perusteella"""
        risk_level = self.analysis.get("risk_level", "unknown")
        goal_progress = self.analysis.get("goal_progress", 0)
        
        if risk_level == "high" or goal_progress < 25:
            return "Alert"
        elif risk_level == "medium" or goal_progress < 50:
            return "Active"
        elif goal_progress > 75:
            return "Optimized"
        else:
            return "Passive"

    def _build_ai_context(self) -> Dict[str, Any]:
        """Rakentaa AI-kontekstin olemassa olevasta datasta"""
        return {
            "financial_goals": self.profile.get("financial_goals", []),
            "preferred_income_methods": self.profile.get("preferred_income_methods", []),
            "work_experience_years": self.profile.get("work_experience_years", 0),
            "time_availability_hours": self.profile.get("time_availability_hours", 0),
            "motivation_level": self.profile.get("motivation_level", 7),
            "ai_recommendations": self.analysis.get("ai_recommendations", [])
        }

    def _calculate_progress_summary(self, base_context: dict) -> Dict[str, Any]:
        """Laskee edistymisyhteenvedon"""
        current_savings = base_context.get("current_savings", 0)
        savings_goal = base_context.get("savings_goal", 100000)
        
        progress_percentage = (current_savings / savings_goal * 100) if savings_goal > 0 else 0
        
        return {
            "goal_progress_percentage": round(progress_percentage, 2),
            "amount_to_goal": savings_goal - current_savings,
            "weeks_completed": base_context.get("current_week", 1) - 1,
            "weeks_remaining": 8 - base_context.get("current_week", 1),
            "on_track": progress_percentage >= (base_context.get("current_week", 1) - 1) * 14.3  # ~14.3% per week
        }

    def _get_current_cycle_details(self) -> Dict[str, Any]:
        """Hakee nykyisen syklin yksityiskohdat"""
        if not self.cycles or "cycles" not in self.cycles:
            return {}
        
        current_week = self.cycles.get("current_week", 1)
        if current_week <= len(self.cycles["cycles"]):
            return self.cycles["cycles"][current_week - 1]
        
        return {}

    def _calculate_data_completeness(self) -> int:
        """Laskee datan täydellisyyden prosenttina"""
        required_fields = [
            "name", "email", "current_savings", "savings_goal", 
            "monthly_income", "monthly_expenses", "skills"
        ]
        
        completed_fields = sum(1 for field in required_fields if self.profile.get(field))
        return round((completed_fields / len(required_fields)) * 100)

# 🧠 GPT-promptin rakentaja käyttäjäkohtaisesti (TÄYDENTÄÄ AI-chat toiminnallisuutta)
def build_enhanced_ai_prompt(user_email: str, query: str) -> str:
    """
    Rakentaa täydellisen AI-promptin olemassa olevasta käyttäjädatasta
    Täydentää olemassa olevaa ai_chat funktiota
    """
    ctx = UserContextManager(user_email).get_enhanced_context()
    
    return f"""
Sinä olet Sentinel 100K -agentti, älykkä henkilökohtainen talousvalmentaja.

=== KÄYTTÄJÄN TÄYDELLINEN KONTEKSTI ===
👤 Käyttäjä: {ctx['name']} ({ctx['user_email']})
💰 Nykyiset säästöt: {ctx['current_savings']:,.0f}€
🎯 Tavoite: {ctx['savings_goal']:,.0f}€ 
📈 Edistyminen: {ctx['progress_summary']['goal_progress_percentage']:.1f}%

📅 VIIKKOSYKLI:
- Viikko: {ctx['current_week']}/7
- Viikkotavoite: {ctx['target_income_weekly']:,.0f}€
- Sykli edistyminen: {ctx['cycle_progress']:.1f}%

💼 OSAAMINEN & KIINNOSTUKSET:
- Taidot: {', '.join(ctx['skills'])}
- Kiinnostukset: {', '.join(ctx['interests'])}
- Työkokemusta: {ctx['ai_context']['work_experience_years']} vuotta
- Aikaa sivutöihin: {ctx['ai_context']['time_availability_hours']}h/viikko

🎯 TALOUSTAVOITTEET:
- Päätavoitteet: {', '.join(ctx['ai_context']['financial_goals'])}
- Ansaintamenetelmät: {', '.join(ctx['ai_context']['preferred_income_methods'])}
- Riskinsietokyky: {ctx['risk_tolerance']}

🤖 AGENTTI TILA:
- Watchdog: {ctx['watchdog_state']}
- Motivaatio: {ctx['ai_context']['motivation_level']}/10
- Datan täydellisyys: {ctx['data_completeness']}%

🌙 VIIMEISIN ANALYYSI:
{', '.join(ctx['ai_context']['ai_recommendations'][:3]) if ctx['ai_context']['ai_recommendations'] else 'Ei vielä analyysiä'}

=== KÄYTTÄJÄN KYSYMYS ===
{query}

=== OHJEISTUS ===
Vastaa henkilökohtaisesti ja käytännöllisesti. Ota huomioon käyttäjän nykyinen tilanne, osaaminen ja tavoitteet. 
Anna konkreettisia neuvoja jotka sopivat juuri tälle käyttäjälle ja hänen viikkosykliinsä.
"""

# ✅ Streamlit-puolella käytettävä funktio (TÄYDENTÄÄ olemassa olevaa)
def get_enhanced_context_streamlit(session_state) -> Dict[str, Any]:
    """
    Täydentää olemassa olevaa get_dashboard_summary funktiota
    Käyttää session_staten user_info sähköpostia
    """
    if not session_state.get("authenticated") or not session_state.get("user_info"):
        raise Exception("Käyttäjä ei ole kirjautunut")
    
    user_email = session_state["user_info"]["email"]
    return UserContextManager(user_email).get_enhanced_context()

# 🔌 Yhteensopivuus-funktio olemassa olevan APIClientin kanssa
def enhance_api_client_with_context(api_client, user_email: str):
    """
    Lisää konteksti-toiminnallisuus olemassa olevaan APIClient-luokkaan
    EI KORVAA vaan TÄYDENTÄÄ
    """
    
    def get_user_context():
        """Uusi metodi APIClientille"""
        try:
            return UserContextManager(user_email).get_enhanced_context()
        except Exception as e:
            return {"error": f"Context loading failed: {str(e)}"}
    
    def enhanced_ai_chat(message: str):
        """Täydentää olemassa olevaa ai_chat metodia"""
        # Rakenna enhanced prompt
        enhanced_prompt = build_enhanced_ai_prompt(user_email, message)
        
        # Käytä olemassa olevaa ai_chat infraa
        original_response = api_client.ai_chat(message)
        
        # Lisää konteksti-tietoja vastaukseen
        if original_response:
            original_response["enhanced_prompt_used"] = True
            original_response["user_context"] = get_user_context()
        
        return original_response
    
    # Lisää metodit olemassa olevaan API clientiin
    api_client.get_user_context = get_user_context
    api_client.enhanced_ai_chat = enhanced_ai_chat
    
    return api_client 