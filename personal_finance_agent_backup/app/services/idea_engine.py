"""
Idea Engine™ - Tienauskoneisto
GPT-moduuli joka ehdottaa päivittäin 1-3 keinoa ansaita lisää rahaa
Räätälöi ehdotuksia kalenterin ja osaamisen mukaan
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
import random
from collections import defaultdict

logger = logging.getLogger(__name__)

class IdeaEngine:
    """
    Idea Engine™ - Älykkäs tienauskoneisto
    
    Generoi päivittäin personoituja ansaintaideoita:
    - Freelance-mahdollisuudet
    - Gig-talous työt
    - Myyntimahdollisuudet
    - Passiivinen tulo
    - Lyhytaikaiset projektit
    """
    
    def __init__(self):
        self.user_profiles = {}  # user_id -> profile data
        self.idea_categories = {
            "freelance": {
                "name": "Freelance & Konsultointi",
                "time_requirement": "2-20h",
                "earning_potential": "50-500€",
                "difficulty": "medium",
                "ideas": [
                    {
                        "title": "Logo-suunnittelu paikallisille yrityksille",
                        "description": "Tarjoa logo- ja brändisuunnittelua pienyrityksille",
                        "skills_needed": ["Graafinen suunnittelu", "Canva/Photoshop"],
                        "platforms": ["Fiverr", "99designs", "Paikallinen Facebook-ryhmä"],
                        "estimated_earning": "100-300€",
                        "time_needed": "3-8h",
                        "difficulty": "medium"
                    },
                    {
                        "title": "Sosiaalisen median sisällöntuotanto",
                        "description": "Luo sisältöä yritysten Instagram/TikTok-tileille",
                        "skills_needed": ["Sisällöntuotanto", "Sosiaalinen media"],
                        "platforms": ["Instagram", "LinkedIn", "Suorat yhteydenotot"],
                        "estimated_earning": "200-800€/kk",
                        "time_needed": "5-15h/viikko",
                        "difficulty": "easy"
                    },
                    {
                        "title": "Verkkosivujen rakentaminen WordPress:llä",
                        "description": "Tee yksinkertaisia verkkosivuja pienyrityksille",
                        "skills_needed": ["WordPress", "Perus-HTML/CSS"],
                        "platforms": ["Upwork", "Freelancer", "Paikallinen markkinointi"],
                        "estimated_earning": "300-1500€",
                        "time_needed": "10-30h",
                        "difficulty": "medium"
                    }
                ]
            },
            "gig_economy": {
                "name": "Gig-talous",
                "time_requirement": "1-8h",
                "earning_potential": "10-100€",
                "difficulty": "easy",
                "ideas": [
                    {
                        "title": "Ruoan kotiinkuljetus viikonloppuisin",
                        "description": "Kuljeta ruokaa Wolt/Foodora-palvelussa",
                        "skills_needed": ["Ajolupa", "Polkupyörä/Auto"],
                        "platforms": ["Wolt", "Foodora"],
                        "estimated_earning": "15-25€/h",
                        "time_needed": "2-8h",
                        "difficulty": "easy"
                    },
                    {
                        "title": "Koirien ulkoilutus naapurustossa",
                        "description": "Tarjoa koiranulkoilutuspalvelua",
                        "skills_needed": ["Koirien kanssa toimiminen"],
                        "platforms": ["Rover", "Paikallinen Facebook", "Ilmoitustaulu"],
                        "estimated_earning": "10-20€/ulkoilutus",
                        "time_needed": "1-2h",
                        "difficulty": "easy"
                    },
                    {
                        "title": "Kauppa-avustus vanhuksille",
                        "description": "Tee ostoksia ikääntyneille naapureille",
                        "skills_needed": ["Luotettavuus", "Auto hyödyksi"],
                        "platforms": ["Vanhustenpalvelut", "Paikallinen ilmoittelu"],
                        "estimated_earning": "20-40€/kerta",
                        "time_needed": "2-3h",
                        "difficulty": "easy"
                    }
                ]
            },
            "selling": {
                "name": "Myynti & Kierrätys",
                "time_requirement": "1-5h",
                "earning_potential": "20-200€",
                "difficulty": "easy",
                "ideas": [
                    {
                        "title": "Käyttämättömien vaatteiden myynti",
                        "description": "Myy kaapin vaatteita verkossa",
                        "skills_needed": ["Valokuvaus", "Tuotekuvaukset"],
                        "platforms": ["Vinted", "Tori.fi", "Facebook Marketplace"],
                        "estimated_earning": "50-300€",
                        "time_needed": "3-6h",
                        "difficulty": "easy"
                    },
                    {
                        "title": "Vintage-löytöjen etsintä ja myynti",
                        "description": "Etsi arvokkaita vintage-esineitä kirppareilta",
                        "skills_needed": ["Tuotetuntemus", "Arviointi"],
                        "platforms": ["Huuto.net", "eBay", "Tori.fi"],
                        "estimated_earning": "100-500€",
                        "time_needed": "4-8h",
                        "difficulty": "medium"
                    },
                    {
                        "title": "Kotitekoisten tuotteiden myynti",
                        "description": "Valmista ja myy käsitöitä",
                        "skills_needed": ["Käsityötaidot", "Luovuus"],
                        "platforms": ["Etsy", "Tori.fi", "Käsityömessut"],
                        "estimated_earning": "100-400€",
                        "time_needed": "5-15h",
                        "difficulty": "medium"
                    }
                ]
            },
            "quick_tasks": {
                "name": "Pikatehtävät",
                "time_requirement": "0.5-3h", 
                "earning_potential": "10-80€",
                "difficulty": "easy",
                "ideas": [
                    {
                        "title": "Kyselytutkimuksiin vastaaminen",
                        "description": "Osallistu maksullisiin kyselyihin",
                        "skills_needed": ["Tietokone/Puhelin"],
                        "platforms": ["Toluna", "Swagbucks", "YouGov"],
                        "estimated_earning": "2-10€/kysely",
                        "time_needed": "10-30min",
                        "difficulty": "easy"
                    },
                    {
                        "title": "Mikrotyöt verkossa",
                        "description": "Tee pieniä tehtäviä verkossa",
                        "skills_needed": ["Tietokoneen käyttö"],
                        "platforms": ["Amazon Mechanical Turk", "Clickworker"],
                        "estimated_earning": "5-20€/h",
                        "time_needed": "1-3h",
                        "difficulty": "easy"
                    },
                    {
                        "title": "Sovellusten testaus",
                        "description": "Testaa uusia sovelluksia ja verkkosivuja",
                        "skills_needed": ["Mobiililaite", "Palautteen antaminen"],
                        "platforms": ["UserTesting", "Testbirds"],
                        "estimated_earning": "10-30€/testi",
                        "time_needed": "30-60min",
                        "difficulty": "easy"
                    }
                ]
            },
            "passive_income": {
                "name": "Passiivinen tulo",
                "time_requirement": "5-40h alkuun",
                "earning_potential": "20-500€/kk",
                "difficulty": "hard",
                "ideas": [
                    {
                        "title": "Osakkeiden osinkosijoittaminen",
                        "description": "Sijoita osinkotuottaviin osakkeisiin",
                        "skills_needed": ["Sijoitustietämys", "Alkupääoma"],
                        "platforms": ["Nordnet", "OP", "Danske Bank"],
                        "estimated_earning": "3-8% vuodessa",
                        "time_needed": "10-20h tutkimusta",
                        "difficulty": "medium"
                    },
                    {
                        "title": "P2P-lainaus",
                        "description": "Lainaa rahaa yksityishenkilöille",
                        "skills_needed": ["Riskinarviointia", "Alkupääoma"],
                        "platforms": ["Bondora", "Mintos"],
                        "estimated_earning": "6-12% vuodessa",
                        "time_needed": "5-15h alkuun",
                        "difficulty": "medium"
                    },
                    {
                        "title": "Online-kurssin luominen",
                        "description": "Luo ja myy omaa osaamistasi kurssina",
                        "skills_needed": ["Asiantuntemus", "Videointi"],
                        "platforms": ["Udemy", "Teachable", "Oma verkkosivusto"],
                        "estimated_earning": "100-1000€/kk",
                        "time_needed": "20-50h luomiseen",
                        "difficulty": "hard"
                    }
                ]
            }
        }
        
        # Päivän mukaan vaihtuvia motivaatioteemoja
        self.daily_themes = {
            0: "momentum_monday",      # Maanantai
            1: "tech_tuesday",         # Tiistai  
            2: "wealth_wednesday",     # Keskiviikko
            3: "thrifty_thursday",     # Torstai
            4: "freelance_friday",     # Perjantai
            5: "selling_saturday",     # Lauantai
            6: "side_hustle_sunday"    # Sunnuntai
        }
        
        self.theme_focus = {
            "momentum_monday": ["gig_economy", "quick_tasks"],
            "tech_tuesday": ["freelance"],
            "wealth_wednesday": ["passive_income"],
            "thrifty_thursday": ["selling"],
            "freelance_friday": ["freelance"],
            "selling_saturday": ["selling"],
            "side_hustle_sunday": ["gig_economy", "quick_tasks"]
        }
    
    def get_daily_ideas(self, user_id: int, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Hae päivittäiset ansaintaideat"""
        try:
            # Päivitä käyttäjäprofiili
            if user_profile:
                self.user_profiles[user_id] = user_profile
            
            # Määritä päivän teema
            weekday = datetime.now().weekday()
            daily_theme = self.daily_themes[weekday]
            focus_categories = self.theme_focus[daily_theme]
            
            # Generoi 3 personoitua ideaa
            ideas = self._generate_personalized_ideas(user_id, focus_categories, 3)
            
            # Lisää päivän erityistarjous
            special_opportunity = self._get_special_opportunity(daily_theme)
            
            # Luo motivoiva viesti
            motivational_message = self._get_daily_motivation(daily_theme)
            
            return {
                "status": "success",
                "daily_theme": daily_theme,
                "ideas": ideas,
                "special_opportunity": special_opportunity,
                "motivational_message": motivational_message,
                "total_potential_earning": sum(self._parse_earning(idea.get("estimated_earning", "0€")) for idea in ideas),
                "estimated_time": self._calculate_total_time(ideas)
            }
            
        except Exception as e:
            logger.error(f"Virhe päivittäisten ideoiden haussa: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_personalized_ideas(self, user_id: int, focus_categories: List[str], count: int) -> List[Dict[str, Any]]:
        """Generoi personoituja ideoita"""
        user_profile = self.user_profiles.get(user_id, {})
        available_time = user_profile.get("available_time_hours", 5)
        skill_level = user_profile.get("skill_level", "beginner")
        preferred_categories = user_profile.get("preferred_categories", focus_categories)
        
        all_ideas = []
        
        # Kerää ideat fokuskategorioista
        for category in focus_categories:
            if category in self.idea_categories:
                category_ideas = self.idea_categories[category]["ideas"]
                for idea in category_ideas:
                    # Suodata käyttäjän profiilin mukaan
                    if self._matches_user_profile(idea, user_profile):
                        idea_copy = idea.copy()
                        idea_copy["category"] = category
                        idea_copy["personalization_score"] = self._calculate_personalization_score(idea, user_profile)
                        all_ideas.append(idea_copy)
        
        # Lisää muutama idea muista kategorioista
        for category, data in self.idea_categories.items():
            if category not in focus_categories:
                best_idea = max(data["ideas"], key=lambda x: self._calculate_personalization_score(x, user_profile))
                if self._matches_user_profile(best_idea, user_profile):
                    idea_copy = best_idea.copy()
                    idea_copy["category"] = category
                    idea_copy["personalization_score"] = self._calculate_personalization_score(best_idea, user_profile)
                    all_ideas.append(idea_copy)
        
        # Järjestä personalisaatiopisteiden mukaan ja valitse parhaat
        sorted_ideas = sorted(all_ideas, key=lambda x: x["personalization_score"], reverse=True)
        
        return sorted_ideas[:count]
    
    def _matches_user_profile(self, idea: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """Tarkista sopiiko idea käyttäjäprofiiliin"""
        available_time = user_profile.get("available_time_hours", 5)
        skill_level = user_profile.get("skill_level", "beginner")
        
        # Tarkista aikarajoite
        idea_time = self._parse_time_requirement(idea.get("time_needed", "5h"))
        if idea_time > available_time:
            return False
        
        # Tarkista taitotaso
        idea_difficulty = idea.get("difficulty", "easy")
        if skill_level == "beginner" and idea_difficulty == "hard":
            return False
        
        return True
    
    def _calculate_personalization_score(self, idea: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Laske personalisaatiopisteet idealle"""
        score = 0.0
        
        # Taitotason mukaisuus
        skill_level = user_profile.get("skill_level", "beginner")
        idea_difficulty = idea.get("difficulty", "easy")
        
        if skill_level == "advanced" and idea_difficulty == "hard":
            score += 3.0
        elif skill_level == "intermediate" and idea_difficulty == "medium":
            score += 2.0
        elif skill_level == "beginner" and idea_difficulty == "easy":
            score += 1.5
        
        # Tuottopotentiaali
        earning = self._parse_earning(idea.get("estimated_earning", "0€"))
        score += min(earning / 100, 3.0)  # Max 3 pistettä tuotoista
        
        # Aikasijoituksen tehokkuus (€/h)
        time_needed = self._parse_time_requirement(idea.get("time_needed", "5h"))
        if time_needed > 0:
            hourly_rate = earning / time_needed
            score += min(hourly_rate / 20, 2.0)  # Max 2 pistettä tuntipalkasta
        
        # Käyttäjän mieltymykset
        preferred_skills = user_profile.get("skills", [])
        idea_skills = idea.get("skills_needed", [])
        skill_match = len(set(preferred_skills) & set(idea_skills)) / max(len(idea_skills), 1)
        score += skill_match * 2.0
        
        return score
    
    def _parse_earning(self, earning_str: str) -> float:
        """Parsii tuotto-merkkijono numeroksi"""
        try:
            # Ota ensimmäinen numero merkkijonosta
            import re
            numbers = re.findall(r'\d+', earning_str)
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0
    
    def _parse_time_requirement(self, time_str: str) -> float:
        """Parsii aikasijoitus tunneiksi"""
        try:
            import re
            numbers = re.findall(r'\d+', time_str)
            if 'min' in time_str.lower():
                return float(numbers[0]) / 60 if numbers else 1.0
            else:
                return float(numbers[0]) if numbers else 5.0
        except:
            return 5.0
    
    def _get_special_opportunity(self, daily_theme: str) -> Dict[str, Any]:
        """Hae päivän erityismahdollisuus"""
        special_opportunities = {
            "momentum_monday": {
                "title": "Maanantai-boost: Aloita viikko ansaitsemalla!",
                "description": "Rekisteröidy uuteen gig-alustaan ja saa bonus",
                "action": "Rekisteröidy Wolt-kuljettajaksi ja ansaitse 50€ bonus",
                "potential_earning": "50-100€",
                "deadline": "Tänään"
            },
            "tech_tuesday": {
                "title": "Tech Tuesday: Teknologia-osaaminen rahaksi",
                "description": "Tarjoa teknistä apua paikallisesti",
                "action": "Luo ilmoitus tietokoneavusta naapurustoon",
                "potential_earning": "30-80€",
                "deadline": "Tällä viikolla"
            },
            "wealth_wednesday": {
                "title": "Wealth Wednesday: Sijoitusmahdollisuus",
                "description": "Tutki uusia sijoitusvaihtoehtoja",
                "action": "Avaa sijoitustili ja aloita osinkosijoittaminen",
                "potential_earning": "Passiivista tuloa",
                "deadline": "Tässä kuussa"
            },
            "thrifty_thursday": {
                "title": "Thrifty Thursday: Säästä ja ansaitse",
                "description": "Kierrätä ja ansaitse samalla",
                "action": "Käy läpi vaatekaappi ja myy Vintedissä",
                "potential_earning": "50-200€",
                "deadline": "Viikonloppuun mennessä"
            },
            "freelance_friday": {
                "title": "Freelance Friday: Vapaa-ajan ansaintaa",
                "description": "Aloita freelance-ura viikonlopuksi",
                "action": "Luo profiili Fiverriin ja tarjoa palveluitasi",
                "potential_earning": "100-500€",
                "deadline": "Ensi viikolla"
            },
            "selling_saturday": {
                "title": "Selling Saturday: Myyntipäivä",
                "description": "Myy kaikki turhat tavarat",
                "action": "Järjestä kotikirppis tai myy netissä",
                "potential_earning": "100-300€",
                "deadline": "Tänään"
            },
            "side_hustle_sunday": {
                "title": "Side Hustle Sunday: Sivubisneksen suunnittelu",
                "description": "Suunnittele pitkäaikaista sivutuloa",
                "action": "Luo suunnitelma säännölliselle sivutulolle",
                "potential_earning": "200-1000€/kk",
                "deadline": "Ensi kuussa"
            }
        }
        
        return special_opportunities.get(daily_theme, special_opportunities["momentum_monday"])
    
    def _get_daily_motivation(self, daily_theme: str) -> str:
        """Hae päivän motivoiva viesti"""
        motivational_messages = {
            "momentum_monday": "💪 Maanantai on uuden alun päivä! Aloita viikko ansaitsemalla ensimmäiset euroesi 100k€ tavoitetta kohti!",
            "tech_tuesday": "💻 Teknologia-osaamisesi on kultaa! Muuta taitosi rahaksi ja vie tavoitettasi eteenpäin!",
            "wealth_wednesday": "💰 Keskiviikko on varallisuuden rakentamisen päivä! Jokainen euro sijoituksissa kasvaa ajan myötä!",
            "thrifty_thursday": "♻️ Kierrätä älykkäästi! Toisen romu on toisen aarre - ja sinun ansaintamahdollisuus!",
            "freelance_friday": "🚀 Perjantai on freelancen kultakausi! Viikonlopun projektit voivat tuoda satoja euroja!",
            "selling_saturday": "🛍️ Lauantai on myyntipäivä! Ihmiset ostavat viikonloppuisin - hyödynnä tilaisuus!",
            "side_hustle_sunday": "🎯 Sunnuntai on suunnittelun päivä! Luo pohja tulevalle viikolle ja pitkäaikaiselle menestykselle!"
        }
        
        return motivational_messages.get(daily_theme, "💡 Tänään on täydellinen päivä ansaita lisää rahaa 100k€ tavoitetta kohti!")
    
    def _calculate_total_time(self, ideas: List[Dict[str, Any]]) -> str:
        """Laske ideoiden kokonaisaika"""
        total_hours = sum(self._parse_time_requirement(idea.get("time_needed", "0h")) for idea in ideas)
        
        if total_hours < 1:
            return f"{int(total_hours * 60)} minuuttia"
        elif total_hours < 8:
            return f"{total_hours:.1f} tuntia"
        else:
            return f"{int(total_hours)} tuntia"
    
    def create_action_plan(self, selected_ideas: List[Dict[str, Any]], user_schedule: Dict[str, Any] = None) -> Dict[str, Any]:
        """Luo toimintasuunnitelma valituille ideoille"""
        try:
            action_plan = {
                "status": "success",
                "plan_created": datetime.now().isoformat(),
                "total_ideas": len(selected_ideas),
                "estimated_total_earning": sum(self._parse_earning(idea.get("estimated_earning", "0€")) for idea in selected_ideas),
                "estimated_total_time": self._calculate_total_time(selected_ideas),
                "daily_schedule": []
            }
            
            # Jaa ideat päivien mukaan käyttäjän aikataulun perusteella
            available_days = user_schedule.get("available_days", 7) if user_schedule else 7
            daily_time_limit = user_schedule.get("daily_time_limit", 3) if user_schedule else 3
            
            current_day = 1
            current_day_time = 0
            current_day_ideas = []
            
            for idea in selected_ideas:
                idea_time = self._parse_time_requirement(idea.get("time_needed", "0h"))
                
                # Jos idea ei mahdu tähän päivään, aloita uusi päivä
                if current_day_time + idea_time > daily_time_limit and current_day_ideas:
                    action_plan["daily_schedule"].append({
                        "day": current_day,
                        "ideas": current_day_ideas.copy(),
                        "total_time": current_day_time,
                        "estimated_earning": sum(self._parse_earning(i.get("estimated_earning", "0€")) for i in current_day_ideas)
                    })
                    
                    current_day += 1
                    current_day_time = 0
                    current_day_ideas = []
                
                # Lisää idea nykyiseen päivään
                current_day_ideas.append(idea)
                current_day_time += idea_time
            
            # Lisää viimeinen päivä
            if current_day_ideas:
                action_plan["daily_schedule"].append({
                    "day": current_day,
                    "ideas": current_day_ideas,
                    "total_time": current_day_time,
                    "estimated_earning": sum(self._parse_earning(i.get("estimated_earning", "0€")) for i in current_day_ideas)
                })
            
            # Lisää käytännön vinkit
            action_plan["practical_tips"] = self._get_practical_tips(selected_ideas)
            action_plan["success_metrics"] = self._define_success_metrics(selected_ideas)
            
            return action_plan
            
        except Exception as e:
            logger.error(f"Virhe toimintasuunnitelman luonnissa: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_practical_tips(self, ideas: List[Dict[str, Any]]) -> List[str]:
        """Hae käytännön vinkit ideoiden toteuttamiseen"""
        tips = [
            "📱 Lataa tarvittavat sovellukset etukäteen",
            "📸 Ota hyvät kuvat tuotteistasi - ne myyvät paremmin",
            "⏰ Varaa aikaa ideoiden toteuttamiseen kalenterista",
            "💳 Varmista että maksutiedot ovat kunnossa alustoilla",
            "📝 Pidä kirjaa ansioistasi verotusta varten"
        ]
        
        # Lisää kategoria-spesifisiä vinkkejä
        categories = set(idea.get("category", "") for idea in ideas)
        
        if "freelance" in categories:
            tips.append("💼 Luo ammattimaiset profiilit freelance-alustoille")
            tips.append("⭐ Pyydä asiakkailta arvosteluja laadun varmistamiseksi")
        
        if "selling" in categories:
            tips.append("🛍️ Tutki markkinahintoja ennen myyntiä")
            tips.append("📦 Varmista turvallinen toimitus ja maksu")
        
        if "gig_economy" in categories:
            tips.append("🚗 Pidä ajoneuvosi hyvässä kunnossa")
            tips.append("😊 Hyvä asiakaspalvelu tuo lisää töitä")
        
        return tips[:8]  # Maksimissaan 8 vinkkiä
    
    def _define_success_metrics(self, ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Määritä onnistumisen mittarit"""
        total_potential = sum(self._parse_earning(idea.get("estimated_earning", "0€")) for idea in ideas)
        
        return {
            "target_earnings": total_potential,
            "minimum_acceptable": total_potential * 0.5,
            "excellent_result": total_potential * 1.2,
            "time_efficiency_target": f"{total_potential / max(1, len(ideas)):.0f}€ per idea",
            "completion_deadline": (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y"),
            "success_indicators": [
                "Vähintään yksi idea toteutettu",
                f"Ansaittu vähintään {total_potential * 0.3:.0f}€",
                "Uusia kontakteja tai asiakkaita saatu",
                "Oppimiskokemuksia kerätty"
            ]
        }
    
    def track_idea_performance(self, user_id: int, idea_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Seuraa idean suorituskykyä"""
        try:
            # Tallenna tulokset (tässä yksinkertainen toteutus)
            performance_data = {
                "idea_id": idea_id,
                "user_id": user_id,
                "execution_date": datetime.now().isoformat(),
                "actual_earning": result.get("earning", 0),
                "time_spent": result.get("time_spent", 0),
                "difficulty_rating": result.get("difficulty", 3),  # 1-5
                "satisfaction": result.get("satisfaction", 3),  # 1-5
                "would_repeat": result.get("would_repeat", False),
                "notes": result.get("notes", "")
            }
            
            # Päivitä käyttäjäprofiilia oppimisen perusteella
            self._update_user_profile_from_performance(user_id, performance_data)
            
            return {
                "status": "success",
                "performance_recorded": True,
                "next_recommendations": self._get_next_recommendations(user_id, performance_data)
            }
            
        except Exception as e:
            logger.error(f"Virhe suorituskyvyn seurannassa: {e}")
            return {"status": "error", "message": str(e)}
    
    def _update_user_profile_from_performance(self, user_id: int, performance: Dict[str, Any]):
        """Päivitä käyttäjäprofiilia suorituskyvyn perusteella"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        
        profile = self.user_profiles[user_id]
        
        # Päivitä taitotaso onnistumisten perusteella
        if performance["satisfaction"] >= 4 and performance["actual_earning"] > 50:
            current_level = profile.get("skill_level", "beginner")
            if current_level == "beginner":
                profile["skill_level"] = "intermediate"
            elif current_level == "intermediate":
                profile["skill_level"] = "advanced"
        
        # Tallenna suosikit
        if performance["would_repeat"]:
            favorites = profile.get("favorite_categories", [])
            idea_category = performance.get("category", "")
            if idea_category and idea_category not in favorites:
                favorites.append(idea_category)
                profile["favorite_categories"] = favorites
    
    def _get_next_recommendations(self, user_id: int, last_performance: Dict[str, Any]) -> List[str]:
        """Hae seuraavat suositukset suorituskyvyn perusteella"""
        recommendations = []
        
        earning = last_performance.get("actual_earning", 0)
        satisfaction = last_performance.get("satisfaction", 3)
        
        if earning > 100 and satisfaction >= 4:
            recommendations.append("🎉 Loistavaa! Jatka samankaltaisilla ideoilla")
            recommendations.append("📈 Harkitse saman kategorian laajentamista")
        elif earning > 50:
            recommendations.append("✅ Hyvä alku! Kokeile samankaltaisia ideoita")
        else:
            recommendations.append("💪 Älä luovuta! Kokeile helpompia ideoita ensin")
            recommendations.append("🎯 Keskity yhteen kategoriaan kerrallaan")
        
        if satisfaction < 3:
            recommendations.append("🔄 Kokeile eri tyyppisiä ideoita")
        
        return recommendations 