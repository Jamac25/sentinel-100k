#!/usr/bin/env python3
"""
🧠 ENHANCED USER CONTEXT SYSTEM - PSYKOLOGINEN LAAJENNUS
========================================================
Täydentää olemassa olevaa Sentinel-järjestelmää käyttäjäkontekstilla

PSYKOLOGISET OMINAISUUDET:
✅ Persoonallisuusprofiilit
✅ Motivaatio & Mindset analyysi  
✅ AI Coach persoonallisuus matching
✅ Oppimistyyli-optimointi
✅ Psykologinen coaching-tyyli
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# 📁 Data files - käytetään samoja kuin backend
ONBOARDING_DATA_FILE = "deep_onboarding_data.json"
WEEKLY_CYCLES_FILE = "weekly_cycles_data.json" 
NIGHT_ANALYSIS_FILE = "night_analysis_data.json"
USERS_DB_FILE = "users_database.json"

def load_data(filename: str) -> dict:
    """Load data from JSON file - standalone versio"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return {}

class PsychologicalProfiler:
    """
    Psykologinen profilointi enhanced context systemille
    """
    
    def __init__(self):
        self.personality_types = {
            "ACHIEVER": {
                "name": "Saavuttaja", 
                "emoji": "🎯",
                "traits": ["tavoitteellinen", "määrätietoinen", "tuloshakuinen"],
                "coaching_style": "Haastava ja tavoiteorientoitunut",
                "motivation_triggers": ["edistyminen", "kilpailu", "saavutukset"]
            },
            "ANALYZER": {
                "name": "Analysoija",
                "emoji": "📊", 
                "traits": ["analyyttinen", "harkitseva", "järjestelmällinen"],
                "coaching_style": "Data-perusteinen ja looginen",
                "motivation_triggers": ["ymmärrys", "kontrolli", "turvallisuus"]
            },
            "SOCIALIZER": {
                "name": "Sosiaalinen",
                "emoji": "👥",
                "traits": ["ihmisläheinen", "yhteisöllinen", "empaattinen"], 
                "coaching_style": "Kannustava ja yhteisöllinen",
                "motivation_triggers": ["tuki", "yhteys", "hyväksyntä"]
            },
            "EXPLORER": {
                "name": "Tutkimusmatkailija", 
                "emoji": "🌟",
                "traits": ["utelias", "luova", "mukautuva"],
                "coaching_style": "Inspiroiva ja joustava",
                "motivation_triggers": ["uutuus", "vapaus", "mahdollisuudet"]
            }
        }
        
        self.coaching_personalities = {
            "MOTIVATOR": {
                "name": "Motivaattori",
                "emoji": "💪",
                "style": "Energinen ja kannustava",
                "approach": "Positiivinen vahvistaminen ja kannustus"
            },
            "MENTOR": {
                "name": "Mentori", 
                "emoji": "🧠",
                "style": "Viisas ja ohjaava",
                "approach": "Pitkäjänteinen opastus ja tuki"
            },
            "COACH": {
                "name": "Valmentaja",
                "emoji": "🎯", 
                "style": "Tavoitteellinen ja haastava",
                "approach": "Konkreettiset tavoitteet ja toimenpiteet"
            },
            "ADVISOR": {
                "name": "Neuvonantaja",
                "emoji": "💡",
                "style": "Analyyttinen ja järkevä", 
                "approach": "Fakta-perusteinen neuvonta"
            }
        }
    
    def analyze_personality_from_onboarding(self, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analysoi persoonallisuus onboarding-datan perusteella"""
        
        # Kerää psykologiset mittarit
        motivation_level = onboarding_data.get('motivation_level', 5)
        commitment_level = onboarding_data.get('commitment_level', 5) 
        learning_preference = onboarding_data.get('learning_preference', 'Käytännön harjoittelu')
        support_preference = onboarding_data.get('support_preference', 'Säännöllistä tukea')
        risk_tolerance = onboarding_data.get('risk_tolerance', 'Maltillinen')
        
        # Määritä persoonallisuustyyppi
        personality_scores = {
            "ACHIEVER": 0,
            "ANALYZER": 0, 
            "SOCIALIZER": 0,
            "EXPLORER": 0
        }
        
        # Motivaatio ja sitoutuminen -> ACHIEVER
        if motivation_level >= 8 and commitment_level >= 8:
            personality_scores["ACHIEVER"] += 3
        
        # Analyyttisyys ja riskinsietokyky -> ANALYZER  
        if risk_tolerance == "Konservatiivinen" and learning_preference in ["Lukeminen", "Kurssit"]:
            personality_scores["ANALYZER"] += 3
            
        # Tuen tarve ja yhteisöllisyys -> SOCIALIZER
        if support_preference in ["Paljon tukea", "Jatkuvaa mentorointia"]:
            personality_scores["SOCIALIZER"] += 3
            
        # Riskinsietokyky ja uteliaisuus -> EXPLORER
        if risk_tolerance == "Aggressiivinen" and learning_preference in ["Videot", "Käytännön harjoittelu"]:
            personality_scores["EXPLORER"] += 3
        
        # Valitse dominoiva persoonallisuus
        dominant_personality = max(personality_scores.keys(), key=lambda k: personality_scores[k])
        
        # Jos tasapeli, käytä motivation_level:iä
        if personality_scores[dominant_personality] == 0:
            dominant_personality = "ACHIEVER" if motivation_level >= 7 else "ANALYZER"
        
        return {
            "dominant_personality": dominant_personality,
            "personality_scores": personality_scores,
            "personality_profile": self.personality_types[dominant_personality],
            "psychological_traits": {
                "motivation_level": motivation_level,
                "commitment_level": commitment_level,
                "learning_style": learning_preference,
                "support_needs": support_preference,
                "risk_profile": risk_tolerance
            }
        }
    
    def determine_optimal_coaching_style(self, personality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Määritä optimaalinen coaching-tyyli persoonallisuuden perusteella"""
        
        dominant_personality = personality_analysis.get("dominant_personality", "ACHIEVER")
        psychological_traits = personality_analysis.get("psychological_traits", {})
        
        # Coaching-tyyli persoonallisuuden mukaan
        coaching_mapping = {
            "ACHIEVER": "COACH",
            "ANALYZER": "ADVISOR", 
            "SOCIALIZER": "MENTOR",
            "EXPLORER": "MOTIVATOR"
        }
        
        optimal_coaching = coaching_mapping.get(dominant_personality, "COACH")
        
        # Hienosäätö motivation_level:n perusteella
        motivation = psychological_traits.get("motivation_level", 5)
        if motivation <= 5:
            optimal_coaching = "MOTIVATOR"  # Matala motivaatio -> tarvitsee motivointia
        elif motivation >= 9:
            optimal_coaching = "COACH"      # Korkea motivaatio -> tarvitsee haastetta
        
        return {
            "optimal_coaching_style": optimal_coaching,
            "coaching_profile": self.coaching_personalities[optimal_coaching],
            "personalized_approach": self._generate_personalized_approach(personality_analysis, optimal_coaching)
        }
    
    def _generate_personalized_approach(self, personality_analysis: Dict[str, Any], coaching_style: str) -> Dict[str, Any]:
        """Luo henkilökohtainen coaching-lähestymistapa"""
        
        personality = personality_analysis.get("dominant_personality", "ACHIEVER")
        traits = personality_analysis.get("psychological_traits", {})
        
        # Henkilökohtaiset suositukset
        approach = {
            "communication_style": "",
            "motivation_strategy": "",
            "goal_setting_approach": "",
            "feedback_frequency": "",
            "support_level": ""
        }
        
        if personality == "ACHIEVER":
            approach.update({
                "communication_style": "Suora ja tavoiteorientoitunut",
                "motivation_strategy": "Kilpailu ja saavutukset",
                "goal_setting_approach": "Kunnianhimoiset ja mitattavat tavoitteet",
                "feedback_frequency": "Viikoittain",
                "support_level": "Vähäinen - antaa itsenäisyyttä"
            })
        elif personality == "ANALYZER":
            approach.update({
                "communication_style": "Looginen ja data-perusteinen", 
                "motivation_strategy": "Ymmärrys ja kontrolli",
                "goal_setting_approach": "Järjestelmälliset ja turvalliset tavoitteet",
                "feedback_frequency": "Kuukausittain syvällisesti",
                "support_level": "Kohtalainen - selkeät ohjeet"
            })
        elif personality == "SOCIALIZER":
            approach.update({
                "communication_style": "Empaattinen ja yhteisöllinen",
                "motivation_strategy": "Tuki ja yhteys",
                "goal_setting_approach": "Yhteistyöhön perustuvat tavoitteet", 
                "feedback_frequency": "Päivittäin tai tarpeen mukaan",
                "support_level": "Korkea - jatkuva tuki"
            })
        elif personality == "EXPLORER":
            approach.update({
                "communication_style": "Inspiroiva ja joustava",
                "motivation_strategy": "Uutuus ja mahdollisuudet",
                "goal_setting_approach": "Luovat ja mukautuvat tavoitteet",
                "feedback_frequency": "Epäsäännöllisesti mutta intensiivisesti", 
                "support_level": "Vaihteleva - antaa tilaa kokeilulle"
            })
        
        return approach

class EnhancedUserContextManager:
    """
    Enhanced User Context Manager - PSYKOLOGISELLA PROFILOINNILLA
    Integroitu olemassa olevaan Sentinel-järjestelmään
    """
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.data_key = f"onboarding_{user_email}"
        
        # Initialize psychological profiler
        self.psychological_profiler = PsychologicalProfiler()
        
        # Load existing data
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Lataa olemassa oleva data JSON-tiedostoista"""
        self.onboarding_data = self._load_json_file("deep_onboarding_data.json")
        self.cycles_data = self._load_json_file("weekly_cycles_data.json") 
        self.analysis_data = self._load_json_file("night_analysis_data.json")
        self.users_data = self._load_json_file("users_database.json")
        
        # Get user-specific data
        self.user_profile = self.onboarding_data.get(self.data_key, {})
        self.user_cycles = self.cycles_data.get(self.data_key, {})
        self.user_analysis = self.analysis_data.get("results", {}).get(self.data_key, {})
        self.user_info = self.users_data.get(self.user_email, {})
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Lataa JSON-tiedosto turvallisesti"""
        try:
            file_path = Path(filename)
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Virhe ladattaessa {filename}: {e}")
        return {}
    
    def get_enhanced_context(self) -> Dict[str, Any]:
        """Hae täydellinen käyttäjäkonteksti PSYKOLOGISELLA PROFILOINNILLA"""
        
        # Perus konteksti
        base_context = self._get_base_context()
        
        # UUSI: Psykologinen analyysi
        psychological_analysis = self._get_psychological_analysis()
        
        # UUSI: AI Coach personalization
        ai_coaching = self._get_ai_coaching_profile()
        
        # Yhdistetty enhanced context
        enhanced_context = {
            **base_context,
            "psychological_profile": psychological_analysis,
            "ai_coaching": ai_coaching,
            "enhanced_features": [
                "psychological_profiling", 
                "personalized_coaching",
                "adaptive_communication",
                "motivation_optimization"
            ],
            "context_generated": datetime.now().isoformat(),
            "data_completeness": self._calculate_data_completeness(),
            "psychological_version": "2.0"
        }
        
        return enhanced_context
    
    def _get_base_context(self) -> Dict[str, Any]:
        """Hae perus käyttäjäkonteksti (säilytetään yhteensopivuus)"""
        return {
            "user_email": self.user_email,
            "data_key": self.data_key,
            "user_id": self.user_profile.get("user_id"),
            "name": self.user_profile.get("name"),
            "current_savings": self.user_profile.get("current_savings", 0),
            "savings_goal": self.user_profile.get("savings_goal", 100000),
            "monthly_income": self.user_profile.get("monthly_income", 0),
            "monthly_expenses": self.user_profile.get("monthly_expenses", 0),
            "skills": self.user_profile.get("skills", []),
            "risk_tolerance": self.user_profile.get("risk_tolerance", "Maltillinen"),
            "current_week": self.user_cycles.get("current_week", 1),
            "target_income_weekly": self._calculate_weekly_target(),
            "watchdog_state": self._determine_watchdog_state(),
            "progress_summary": self._calculate_progress_summary()
        }
    
    def _get_psychological_analysis(self) -> Dict[str, Any]:
        """UUSI: Hae psykologinen analyysi"""
        if not self.user_profile:
            return {}
        
        personality_analysis = self.psychological_profiler.analyze_personality_from_onboarding(self.user_profile)
        
        return {
            **personality_analysis,
            "psychological_insights": self._generate_psychological_insights(personality_analysis),
            "motivation_triggers": self._identify_motivation_triggers(personality_analysis),
            "communication_preferences": self._determine_communication_preferences(personality_analysis)
        }
    
    def _get_ai_coaching_profile(self) -> Dict[str, Any]:
        """UUSI: Hae AI coaching-profiili"""
        if not self.user_profile:
            return {}
        
        personality_analysis = self.psychological_profiler.analyze_personality_from_onboarding(self.user_profile)
        coaching_profile = self.psychological_profiler.determine_optimal_coaching_style(personality_analysis)
        
        return {
            **coaching_profile,
            "adaptive_responses": self._generate_adaptive_responses(coaching_profile),
            "personalized_prompts": self._create_personalized_prompts(personality_analysis, coaching_profile)
        }
    
    def _generate_psychological_insights(self, personality_analysis: Dict[str, Any]) -> List[str]:
        """Generoi psykologisia oivalluksia"""
        insights = []
        
        personality = personality_analysis.get("dominant_personality", "ACHIEVER")
        traits = personality_analysis.get("psychological_traits", {})
        
        motivation = traits.get("motivation_level", 5)
        commitment = traits.get("commitment_level", 5)
        
        if motivation >= 8:
            insights.append("Korkea sisäinen motivaatio - hyötyy haastavista tavoitteista")
        elif motivation <= 4:
            insights.append("Tarvitsee ulkoista motivointia ja kannustusta")
        
        if commitment >= 8:
            insights.append("Vahva sitoutumiskyky - sopii pitkäjänteisiin suunnitelmiin")
        elif commitment <= 4:
            insights.append("Hyötyy lyhyistä välitavoitteista ja nopeista voitoista")
        
        personality_traits = self.psychological_profiler.personality_types[personality]["traits"]
        insights.append(f"Persoonallisuus: {', '.join(personality_traits)}")
        
        return insights
    
    def _identify_motivation_triggers(self, personality_analysis: Dict[str, Any]) -> List[str]:
        """Tunnista motivaation laukaisijoita"""
        personality = personality_analysis.get("dominant_personality", "ACHIEVER")
        return self.psychological_profiler.personality_types[personality]["motivation_triggers"]
    
    def _determine_communication_preferences(self, personality_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Määritä viestintämieltymykset"""
        personality = personality_analysis.get("dominant_personality", "ACHIEVER")
        traits = personality_analysis.get("psychological_traits", {})
        
        preferences = {
            "tone": "kannustava",
            "detail_level": "kohtalainen", 
            "frequency": "viikoittain",
            "format": "tekstimuoto"
        }
        
        if personality == "ACHIEVER":
            preferences.update({
                "tone": "haastava ja energinen",
                "detail_level": "toimintaorientoitunut",
                "frequency": "usein",
                "format": "lyhyet ja ytimekkäät viestit"
            })
        elif personality == "ANALYZER":
            preferences.update({
                "tone": "analyyttinen ja rauhallinen",
                "detail_level": "syvällinen", 
                "frequency": "harvemmin mutta perusteellisesti",
                "format": "yksityiskohtaiset raportit"
            })
        elif personality == "SOCIALIZER":
            preferences.update({
                "tone": "empaattinen ja tukeva",
                "detail_level": "henkilökohtainen",
                "frequency": "säännöllisesti",
                "format": "vuorovaikutteiset keskustelut"
            })
        elif personality == "EXPLORER":
            preferences.update({
                "tone": "inspiroiva ja luova", 
                "detail_level": "vaihteleva",
                "frequency": "spontaanisti",
                "format": "visuaaliset ja interaktiiviset"
            })
        
        return preferences
    
    def _generate_adaptive_responses(self, coaching_profile: Dict[str, Any]) -> Dict[str, str]:
        """Luo adaptiivisia vastauksia eri tilanteisiin"""
        coaching_style = coaching_profile.get("optimal_coaching_style", "COACH")
        
        responses = {
            "success_response": "",
            "struggle_response": "", 
            "motivation_response": "",
            "guidance_response": ""
        }
        
        if coaching_style == "MOTIVATOR":
            responses.update({
                "success_response": "💪 Loistavaa! Olet täydellisesti raiteilla!",
                "struggle_response": "🌟 Älä huoli, jokainen mestari kohtaa haasteita! Jatketaan yhdessä!",
                "motivation_response": "🚀 Sinulla on kaikki tarvittava menestykseen! Uskotaan itseemme!",
                "guidance_response": "✨ Kokeillaan uutta lähestymistapaa - sinä pystyt tähän!"
            })
        elif coaching_style == "MENTOR":
            responses.update({
                "success_response": "🧠 Olet oppimassa nopeasti. Tämä on oikea suunta.",
                "struggle_response": "💭 Vaikeudet ovat oppimisen mahdollisuuksia. Analysoidaan yhdessä.",
                "motivation_response": "🎯 Muista miksi aloitit. Kasvu vaatii kärsivällisyyttä.",
                "guidance_response": "📚 Jaksetaan tietoa pienissä paloissa. Etenemme varmasti."
            })
        elif coaching_style == "COACH":
            responses.update({
                "success_response": "🎯 Erinomaista suoritusta! Nostetaan rimaa vielä korkeammalle!",
                "struggle_response": "💪 Tämä on testi. Näytetään mitä sinussa on!",
                "motivation_response": "🏆 Champions are made in moments like this. Fokus ja toiminta!",
                "guidance_response": "📊 Strategia on selvä. Toteutetaan suunnitelma askeleittain."
            })
        elif coaching_style == "ADVISOR":
            responses.update({
                "success_response": "📊 Data vahvistaa edistymisesi. Jatka samalla strategialla.",
                "struggle_response": "📈 Analysoidaan tilanne objektiivisesti ja mukautetaan lähestymistapaa.",
                "motivation_response": "💡 Loogisesti ajateltuna sinulla on kaikki edellytykset menestykseen.",
                "guidance_response": "🔍 Tutkitaan vaihtoehdot huolellisesti ennen päätöstä."
            })
        
        return responses
    
    def _create_personalized_prompts(self, personality_analysis: Dict[str, Any], coaching_profile: Dict[str, Any]) -> Dict[str, str]:
        """Luo henkilökohtaiset AI-promptit"""
        personality = personality_analysis.get("dominant_personality", "ACHIEVER")
        coaching_style = coaching_profile.get("optimal_coaching_style", "COACH")
        traits = personality_analysis.get("psychological_traits", {})
        
        personality_info = self.psychological_profiler.personality_types[personality]
        coaching_info = self.psychological_profiler.coaching_personalities[coaching_style]
        
        prompts = {
            "system_prompt": f"""
Sinä olet {coaching_info['name']} {coaching_info['emoji']}, henkilökohtainen rahoitusvalmentaja.

KÄYTTÄJÄN PSYKOLOGINEN PROFIILI:
- Persoonallisuus: {personality_info['name']} {personality_info['emoji']}
- Luonteenpiirteet: {', '.join(personality_info['traits'])}
- Motivaatiotaso: {traits.get('motivation_level', 5)}/10
- Sitoutumistaso: {traits.get('commitment_level', 5)}/10
- Oppimistyyli: {traits.get('learning_style', 'Käytännön harjoittelu')}
- Tuen tarve: {traits.get('support_needs', 'Säännöllistä tukea')}

COACHING-TYYLISI:
- Lähestymistapa: {coaching_info['style']}
- Metodi: {coaching_info['approach']}
- Motivaation laukaisijoita: {', '.join(personality_info['motivation_triggers'])}

Vastaa AINA tässä tyylissä ja ota huomioon käyttäjän psykologinen profiili.
""",
            
            "response_template": f"""
{coaching_info['emoji']} **{coaching_info['name']}-vastaus {personality_info['name']}-tyypille:**

[Henkilökohtainen vastaus perustuen psykologiseen profiiliin]

🎯 **Räätälöity toimenpide:**
[Persoonallisuuden mukainen suositus]

💭 **Psykologinen tuki:**
[Motivaation ja mieltymysten mukainen kannustus]
""",

            "motivation_prompt": f"""
Motivoi {personality_info['name']}-tyyppistä käyttäjää käyttäen näitä laukaisijoita:
{', '.join(personality_info['motivation_triggers'])}

Coaching-tyyli: {coaching_info['style']}
Henkilön motivaatiotaso: {traits.get('motivation_level', 5)}/10
""",

            "guidance_prompt": f"""
Anna henkilökohtaista ohjausta {personality_info['name']}-tyypille.
Oppimistyyli: {traits.get('learning_style', 'Käytännön harjoittelu')}
Tuen tarve: {traits.get('support_needs', 'Säännöllistä tukea')}
Käytä {coaching_info['approach']} -lähestymistapaa.
"""
        }
        
        return prompts
    
    # Säilytetään yhteensopivuus vanhojen metodien kanssa
    def _calculate_weekly_target(self) -> float:
        """Laske viikkotavoite"""
        monthly_income = self.user_profile.get("monthly_income", 3000)
        return max(300, monthly_income / 4 * 0.25)
    
    def _determine_watchdog_state(self) -> str:
        """Määritä watchdog-tila"""
        current_savings = self.user_profile.get("current_savings", 0)
        savings_goal = self.user_profile.get("savings_goal", 100000)
        progress = (current_savings / savings_goal * 100) if savings_goal > 0 else 0
        
        if progress < 25:
            return "Alert"
        elif progress < 50:
            return "Active"
        elif progress > 75:
            return "Optimized"
        else:
            return "Passive"
    
    def _calculate_progress_summary(self) -> Dict[str, Any]:
        """Laske edistymisyhteenveto"""
        current_savings = self.user_profile.get("current_savings", 0)
        savings_goal = self.user_profile.get("savings_goal", 100000)
        current_week = self.user_cycles.get("current_week", 1)
        
        progress_percentage = (current_savings / savings_goal * 100) if savings_goal > 0 else 0
        
        return {
            "goal_progress_percentage": round(progress_percentage, 2),
            "amount_to_goal": savings_goal - current_savings,
            "weeks_completed": current_week - 1,
            "weeks_remaining": 8 - current_week,
            "on_track": progress_percentage >= (current_week - 1) * 14.3
        }
    
    def _calculate_data_completeness(self) -> int:
        """Laske datan täydellisyys"""
        required_fields = [
            "name", "email", "current_savings", "savings_goal", 
            "monthly_income", "monthly_expenses", "skills",
            "motivation_level", "commitment_level", "learning_preference"
        ]
        
        completed_fields = sum(1 for field in required_fields if self.user_profile.get(field))
        return round((completed_fields / len(required_fields)) * 100)

# Compatibility function
def get_enhanced_context_streamlit(session_state) -> Dict[str, Any]:
    """
    Streamlit-yhteensopiva funktio enhanced context hakemiseen
    PSYKOLOGISELLA PROFILOINNILLA
    """
    user_email = session_state.get('user_info', {}).get('email', 'demo@example.com')
    
    context_manager = EnhancedUserContextManager(user_email)
    enhanced_context = context_manager.get_enhanced_context()
    
    # Lisää Streamlit-spesifiset kentät
    enhanced_context.update({
        "compatibility": "Integroitu olemassa olevaan Sentinel-järjestelmään",
        "version": "2.0-psychological",
        "data_sources": [
            "deep_onboarding_data.json",
            "weekly_cycles_data.json", 
            "night_analysis_data.json",
            "users_database.json"
        ],
        "context_features": [
            "user_profile",
            "weekly_cycles",
            "night_analysis", 
            "watchdog_state",
            "progress_summary",
            "ai_context",
            "psychological_profile",  # UUSI
            "ai_coaching",            # UUSI
            "personalized_prompts"    # UUSI
        ]
    })
    
    return enhanced_context

# Main demo function
def main():
    """Demo enhanced context systemistä psykologisella profiloinnilla"""
    print("🧠 ENHANCED CONTEXT SYSTEM - PSYKOLOGINEN LAAJENNUS")
    print("="*60)
    
    # Test with demo user
    context_manager = EnhancedUserContextManager("demo@example.com")
    enhanced_context = context_manager.get_enhanced_context()
    
    print("👤 Käyttäjä:", enhanced_context.get('name', 'N/A'))
    print("📊 Edistyminen:", f"{enhanced_context.get('progress_summary', {}).get('goal_progress_percentage', 0):.1f}%")
    print("🤖 Watchdog:", enhanced_context.get('watchdog_state', 'N/A'))
    
    # Show psychological profile
    psychological = enhanced_context.get('psychological_profile', {})
    if psychological:
        print("\n🧠 PSYKOLOGINEN PROFIILI:")
        personality = psychological.get('dominant_personality', 'N/A')
        print(f"  Persoonallisuus: {personality}")
        
        traits = psychological.get('psychological_traits', {})
        print(f"  Motivaatio: {traits.get('motivation_level', 'N/A')}/10")
        print(f"  Sitoutuminen: {traits.get('commitment_level', 'N/A')}/10")
        
        insights = psychological.get('psychological_insights', [])
        if insights:
            print("  Oivalluksia:")
            for insight in insights:
                print(f"    • {insight}")
    
    # Show AI coaching profile
    ai_coaching = enhanced_context.get('ai_coaching', {})
    if ai_coaching:
        print("\n🤖 AI COACHING PROFIILI:")
        coaching_style = ai_coaching.get('optimal_coaching_style', 'N/A')
        print(f"  Coaching-tyyli: {coaching_style}")
        
        coaching_profile = ai_coaching.get('coaching_profile', {})
        if coaching_profile:
            print(f"  Emoji: {coaching_profile.get('emoji', '🤖')}")
            print(f"  Nimi: {coaching_profile.get('name', 'N/A')}")
            print(f"  Tyyli: {coaching_profile.get('style', 'N/A')}")

if __name__ == "__main__":
    main() 