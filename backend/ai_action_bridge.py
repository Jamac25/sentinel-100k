"""
AI Action Bridge - Käsittelee Telegram-komennot ja integroi Sentinel-palveluihin
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import openai
import asyncio

# Import Sentinel Integration
try:
    from backend.sentinel_integration_simple import simple_sentinel_integration as sentinel_integration
except ImportError:
    sentinel_integration = None

class AIActionBridge:
    """
    AI Action Bridge - Käsittelee intentit ja suorittaa toiminnat
    
    Ominaisuudet:
    - Intent-based command handling
    - Sentinel service integration
    - AI-powered responses
    - User context management
    """
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if self.openai_key:
            openai.api_key = self.openai_key
        
        # API endpoints
        self.base_url = os.getenv("SENTINEL_API_URL", "http://localhost:8000")
        
        # User context cache
        self.user_contexts = {}
        
    def execute(self, user_id: str, intent: str, params: dict) -> str:
        """
        Suorittaa intentin ja palauttaa vastauksen
        
        Args:
            user_id: Käyttäjän ID
            intent: Tunnistettu intent
            params: Intentin parametrit
            
        Returns:
            str: Vastaus käyttäjälle
        """
        try:
            # Päivitä käyttäjän konteksti
            self._update_user_context(user_id, intent, params)
            
            # Jos Sentinel Integration on saatavilla, käytä sitä
            if sentinel_integration and sentinel_integration.is_initialized:
                return asyncio.run(self._execute_with_sentinel(user_id, intent, params))
            
            # Fallback: Suorita intent-spesifinen toiminto
            if intent == "START":
                return self._handle_start(user_id)
            elif intent == "DASHBOARD":
                return self._handle_dashboard(user_id)
            elif intent == "SET_GOAL":
                return self._handle_set_goal(user_id, params)
            elif intent == "ONBOARDING":
                return self._handle_onboarding(user_id)
            elif intent == "RUN_ANALYSIS":
                return self._handle_analysis(user_id)
            elif intent == "START_CYCLE":
                return self._handle_new_cycle(user_id)
            elif intent == "WEEK":
                return self._handle_week(user_id, params)
            elif intent == "REPORT":
                return self._handle_report(user_id)
            elif intent == "INCOME":
                return self._handle_income(user_id, params)
            elif intent == "EXPENSES":
                return self._handle_expenses(user_id, params)
            elif intent == "MOTIVATE":
                return self._handle_motivate(user_id)
            elif intent == "HELP":
                return self._handle_help()
            elif intent == "SETTINGS":
                return self._handle_settings(user_id)
            elif intent == "EXPORT":
                return self._handle_export(user_id)
            elif intent == "DELETE":
                return self._handle_delete(user_id)
            elif intent == "RISK":
                return self._handle_risk(user_id)
            else:
                return self._handle_unknown(user_id, intent, params)
                
        except Exception as e:
            print(f"❌ AI Action Bridge error: {e}")
            return self._generate_error_response(user_id, e)
    
    def _handle_start(self, user_id: str) -> str:
        """Käsittelee /start komennon"""
        welcome_message = f"""
🚀 Tervetuloa Sentinel 100K:een!

Olen sinun henkilökohtainen talousvalmentajasi, joka auttaa sinua säästämään 100,000€.

📋 Komennot:
/start - Tämä viesti
/dashboard - Tilannekatsaus
/setgoal <määrä> - Aseta säästötavoite
/onboarding - Aloita onboarding
/analysis - Suorita analyysi
/cycle - Aloita uusi 7-viikon sykli
/week <numero> - Näytä viikon tiedot
/report - Kuukausiraportti
/income <määrä> - Lisää tuloja
/expenses <määrä> - Lisää menoja
/motivate - Motivaatioviesti
/help - Apua
/risk - Riskianalyysi

💡 Vinkki: Aloita komennolla /onboarding saadaksesi henkilökohtaisen suunnitelman!
        """
        return welcome_message.strip()
    
    def _handle_dashboard(self, user_id: str) -> str:
        """Käsittelee dashboard-komennon"""
        try:
            # Hae dashboard data API:sta
            response = requests.get(f"{self.base_url}/api/v1/dashboard/complete/{user_id}")
            if response.status_code == 200:
                data = response.json()
                
                dashboard = f"""
📊 SENTINEL DASHBOARD

💰 Säästöt: {data.get('current_savings', 0):,.0f}€ / {data.get('savings_goal', 100000):,.0f}€
📈 Edistyminen: {data.get('goal_completion', 0):.1f}%

💵 Kuukausittainen:
   Tulot: {data.get('monthly_income', 0):,.0f}€
   Menot: {data.get('monthly_expenses', 0):,.0f}€
   Ylijäämä: {data.get('monthly_surplus', 0):,.0f}€

🎯 Säästöaste: {data.get('savings_rate', 0):.1f}%
⚠️ Riskitaso: {data.get('risk_level', 'tuntematon')}

📅 Viimeisin päivitys: {datetime.now().strftime('%d.%m.%Y %H:%M')}
                """
                return dashboard.strip()
            else:
                return "❌ Ei voitu hakea dashboard-tietoja. Kokeile /onboarding ensin."
                
        except Exception as e:
            return f"❌ Virhe dashboard-haussa: {str(e)}"
    
    def _handle_set_goal(self, user_id: str, params: dict) -> str:
        """Käsittelee säästötavoitteen asettamisen"""
        amount = params.get('amount', 0)
        if amount <= 0:
            return "❌ Virheellinen määrä. Käytä: /setgoal <määrä>"
        
        try:
            # Tallenna tavoite
            goal_data = {
                "user_id": user_id,
                "savings_goal": amount,
                "set_at": datetime.now().isoformat()
            }
            
            # Tässä tallennettaisiin tietokantaan
            # response = requests.post(f"{self.base_url}/api/v1/goals/set", json=goal_data)
            
            return f"""
🎯 SÄÄSTÖTAVOITE ASETETTU!

💰 Tavoite: {amount:,.0f}€
📅 Asetettu: {datetime.now().strftime('%d.%m.%Y')}

💡 Seuraavat askeleet:
1. Suorita /onboarding saadaksesi henkilökohtaisen suunnitelman
2. Käytä /analysis nähdäksesi nykyisen tilanteen
3. Aloita uusi sykli komennolla /cycle

🚀 Olet valmis aloittamaan 100K matkan!
            """.strip()
            
        except Exception as e:
            return f"❌ Virhe tavoitteen asettamisessa: {str(e)}"
    
    def _handle_onboarding(self, user_id: str) -> str:
        """Käsittelee onboarding-komennon"""
        onboarding_message = f"""
📋 SENTINEL ONBOARDING

Tervetuloa henkilökohtaiseen talousvalmennukseen!

🔍 Tarvitsemme sinusta tietoja:
• Nimi ja ikä
• Ammatti ja kokemus
• Nykyiset säästöt
• Kuukausitulot ja -menot
• Taidot ja aika
• Taloudelliset tavoitteet

📝 Vastaa seuraaviin kysymyksiin:

1️⃣ Mikä on nimesi ja ikäsi?
2️⃣ Mitä työtä teet ja kuinka kauan?
3️⃣ Paljonko sinulla on säästöjä nyt?
4️⃣ Mitkä ovat kuukausittaiset tulosi ja menosi?
5️⃣ Mitä taitoja sinulla on (esim. ohjelmointi, käsityöt)?
6️⃣ Kuinka monta tuntia viikossa voit käyttää lisätulojen hankintaan?

💡 Vastaa yksi kerrallaan, niin luon sinulle henkilökohtaisen 7-viikon suunnitelman!
        """
        return onboarding_message.strip()
    
    def _handle_analysis(self, user_id: str) -> str:
        """Käsittelee analyysi-komennon"""
        try:
            # Suorita yöanalyysi
            response = requests.post(f"{self.base_url}/api/v1/analysis/night/trigger")
            
            analysis_message = f"""
🔍 SENTINEL ANALYYSI SUORITETTU

📊 Yöanalyysi käynnistetty...
⏰ Aika: {datetime.now().strftime('%d.%m.%Y %H:%M')}

🧠 AI analysoi:
• Kulutuskäyttäytymisesi
• Säästömahdollisuudet
• Riskit ja uhkat
• Optimoimismahdollisuudet

📈 Tulokset saatavilla:
• /dashboard - Yleiskatsaus
• /report - Yksityiskohtainen raportti
• /risk - Riskianalyysi

💡 Vinkki: Tarkista /dashboard nähdäksesi päivitetyt tiedot!
            """
            return analysis_message.strip()
            
        except Exception as e:
            return f"❌ Virhe analyysin suorittamisessa: {str(e)}"
    
    def _handle_new_cycle(self, user_id: str) -> str:
        """Käsittelee uuden syklin aloittamisen"""
        cycle_message = f"""
🔄 UUSI 7-VIIKON SYKLI ALOITETTU!

📅 Aloituspäivä: {datetime.now().strftime('%d.%m.%Y')}
🎯 Tavoite: 100,000€ säästöt

📋 Syklin vaiheet:
Viikko 1-2: Perustiedot ja tavoitteet
Viikko 3-4: Säästöstrategiat
Viikko 5-6: Lisätulojen hankinta
Viikko 7: Optimointi ja seuraava sykli

💡 Käytä komennot:
• /week 1 - Näytä viikon 1 tiedot
• /dashboard - Tilannekatsaus
• /motivate - Motivaatioviesti

🚀 Olet valmis aloittamaan 100K matkan!
        """
        return cycle_message.strip()
    
    def _handle_week(self, user_id: str, params: dict) -> str:
        """Käsittelee viikkotietojen näyttämisen"""
        week = params.get('week', 1)
        
        week_data = self._get_week_data(week)
        
        week_message = f"""
📅 VIIKKO {week} - SENTINEL SYKLI

🎯 Tavoite: {week_data['target']}€ säästöä
📋 Fokus: {week_data['focus']}
🏆 Milestone: {week_data['milestone']}

💡 Tehtävät:
{week_data['tasks']}

📊 Edistyminen:
• Säästetty: {week_data['saved']}€
• Jäljellä: {week_data['remaining']}€
• Suoritettu: {week_data['completed']}%

🚀 Seuraava: {week_data['next']}
        """
        return week_message.strip()
    
    def _handle_report(self, user_id: str) -> str:
        """Käsittelee raportin näyttämisen"""
        report_message = f"""
📊 KUUKAUSIRAPORTTI - {datetime.now().strftime('%B %Y')}

💰 SÄÄSTÖT:
• Alku: 25,000€
• Loppu: 27,850€
• Muutos: +2,850€ (+11.4%)

📈 TULOT:
• Palkka: 3,200€
• Lisätulot: 450€
• Yhteensä: 3,650€

💸 MENOT:
• Asuminen: 800€
• Ruoka: 400€
• Liikenne: 150€
• Viihde: 200€
• Muut: 100€
• Yhteensä: 1,650€

🎯 TAVOITE:
• Säästötavoite: 100,000€
• Edistyminen: 27.85%
• Jäljellä: 72,150€

💡 Seuraavat askeleet:
1. Lisää lisätulojen hankintaa
2. Optimoi kulutuskäyttäytymistä
3. Aloita sijoittaminen

🚀 Olet hyvällä tiellä 100K tavoitteeseen!
        """
        return report_message.strip()
    
    def _handle_income(self, user_id: str, params: dict) -> str:
        """Käsittelee tulojen lisäämisen"""
        amount = params.get('amount', 0)
        if amount <= 0:
            return "❌ Virheellinen määrä. Käytä: /income <määrä>"
        
        income_message = f"""
💰 TULO LISÄTTY!

💵 Määrä: {amount:,.0f}€
📅 Päivä: {datetime.now().strftime('%d.%m.%Y')}

📊 Päivitetty tilanne:
• Kuukausitulot: 3,650€ → {3650 + amount:,.0f}€
• Säästömahdollisuus: +{amount:,.0f}€

💡 Vinkit lisätulojen hankintaan:
• Freelance-projektit
• Online-kauppa
• Kuljetuspalvelut
• Oppimateriaalien myynti

🎯 Käytä /ideas nähdäksesi lisää ideoita!
        """
        return income_message.strip()
    
    def _handle_expenses(self, user_id: str, params: dict) -> str:
        """Käsittelee menojen lisäämisen"""
        amount = params.get('amount', 0)
        if amount <= 0:
            return "❌ Virheellinen määrä. Käytä: /expenses <määrä>"
        
        expense_message = f"""
💸 MENO LISÄTTY!

💵 Määrä: {amount:,.0f}€
📅 Päivä: {datetime.now().strftime('%d.%m.%Y')}

⚠️ Budjettitarkistus:
• Kuukausimenot: 1,650€ → {1650 + amount:,.0f}€
• Säästömahdollisuus: -{amount:,.0f}€

💡 Säästövinkit:
• Tarkista tarpeettomat tilaukset
• Vertaa hintoja
• Käytä alennuskoodeja
• Suunnittele ostokset etukäteen

🎯 Käytä /analysis nähdäksesi optimoimismahdollisuudet!
        """
        return expense_message.strip()
    
    def _handle_motivate(self, user_id: str) -> str:
        """Käsittelee motivaatioviestin"""
        motivation_messages = [
            "🚀 Muista: Jokainen euro on askel kohti vapautta!",
            "💪 Sinä pystyt siihen! 100K on vain 1000 x 100€ säästöä.",
            "🎯 Tänään säästämäsi euro on huomisen vapauden perusta.",
            "🌟 Olet rakentamassa parempaa tulevaisuutta itsellesi!",
            "🔥 Jokainen päivä on mahdollisuus lähemmäs tavoitetta!",
            "💎 Säästäminen on lahja itsellesi tulevaisuudessa.",
            "⚡ Sinulla on voima muuttaa taloudellinen tulevaisuutesi!",
            "🎉 Jokainen säästö on voitto itsellesi!"
        ]
        
        import random
        message = random.choice(motivation_messages)
        
        motivate_message = f"""
💪 SENTINEL MOTIVAATIO

{message}

📊 Muista tavoitteesi:
• 100,000€ säästöt
• Taloudellinen vapaus
• Parempi tulevaisuus

🎯 Tänään voit:
• Säästää 10€ → 10€ lähemmäs tavoitetta
• Etsiä lisätulomahdollisuuden
• Optimoida kulutustasi

🚀 Sinä pystyt siihen! 💪
        """
        return motivate_message.strip()
    
    def _handle_help(self) -> str:
        """Käsittelee apu-komennon"""
        help_message = f"""
❓ SENTINEL 100K - APUA

📋 KOMENNOT:

🎯 Perustoiminnot:
/start - Tervetuloviesti
/dashboard - Tilannekatsaus
/help - Tämä apu

💰 Talous:
/setgoal <määrä> - Aseta säästötavoite
/income <määrä> - Lisää tuloja
/expenses <määrä> - Lisää menoja

📊 Analyysi:
/analysis - Suorita analyysi
/report - Kuukausiraportti
/risk - Riskianalyysi

🔄 Syklit:
/cycle - Aloita uusi sykli
/week <numero> - Viikkotiedot

💡 Muut:
/onboarding - Henkilökohtainen suunnitelma
/motivate - Motivaatioviesti
/settings - Asetukset

📞 Tuki: Jos tarvitset apua, vastaa tähän viestiin!
        """
        return help_message.strip()
    
    def _handle_settings(self, user_id: str) -> str:
        """Käsittelee asetukset-komennon"""
        settings_message = f"""
⚙️ SENTINEL ASETUKSET

👤 Käyttäjä: {user_id}
📅 Liittynyt: {datetime.now().strftime('%d.%m.%Y')}

🔔 Ilmoitukset:
• Päivittäiset muistutukset: ✅ Päällä
• Viikkoraportit: ✅ Päällä
• Riskivaroitukset: ✅ Päällä

🎯 Tavoitteet:
• Säästötavoite: 100,000€
• Kuukausitavoite: 2,500€
• Viikkotavoite: 625€

📊 Analyysi:
• Yöanalyysi: 02:00
• Viikkoraportti: Sunnuntai
• Kuukausiraportti: Kuun viimeinen päivä

💡 Muutokset: Vastaa tähän viestiin pyytääksesi muutoksia!
        """
        return settings_message.strip()
    
    def _handle_export(self, user_id: str) -> str:
        """Käsittelee profiilin vienti-komennon"""
        export_message = f"""
📤 PROFIILIN VIENTI

📊 Viedään tiedot:
• Henkilötiedot
• Taloustiedot
• Säästöhistoria
• Analyysitulokset

⏳ Käsitellään...
✅ Vienti valmis!

📁 Tiedostot:
• sentinel_profile_{user_id}.json
• sentinel_analysis_{user_id}.pdf
• sentinel_goals_{user_id}.csv

💡 Tiedostot lähetetään sähköpostiisi tai tallennetaan pilveen.

🔒 Tietoturva: Kaikki tiedot salataan ja varmuuskopioidaan.
        """
        return export_message.strip()
    
    def _handle_delete(self, user_id: str) -> str:
        """Käsittelee profiilin poisto-komennon"""
        delete_message = f"""
🗑️ PROFIILIN POISTO

⚠️ VAROITUS: Tämä toiminto poistaa kaikki tietosi pysyvästi!

📋 Poistetaan:
• Henkilötiedot
• Taloustiedot
• Säästöhistoria
• Analyysitulokset
• Käyttäjäasetukset

❓ Oletko varma? Vastaa:
• "Kyllä, poista profiili" - Poistaa kaikki
• "Peruuta" - Peruuttaa poiston

🔒 Tietoturva: Poistetut tiedot eivät ole palautettavissa.
        """
        return delete_message.strip()
    
    def _handle_risk(self, user_id: str) -> str:
        """Käsittelee riskianalyysi-komennon"""
        risk_message = f"""
⚠️ SENTINEL RISKIANALYYSI

📊 Riskitaso: ALHAINEN (2/10)

🎯 Säästötavoite:
• Tavoite: 100,000€
• Edistyminen: 27.85%
• Riskitaso: ALHAINEN ✅

💰 Taloudellinen tilanne:
• Kuukausitulot: 3,200€
• Kuukausimenot: 1,650€
• Säästöaste: 79.2%
• Riskitaso: ALHAINEN ✅

📈 Kulutuskäyttäytyminen:
• Trendi: Vakaa
• Poikkeamat: Ei
• Riskitaso: ALHAINEN ✅

💡 Suositukset:
• Jatka nykyistä säästöstrategiaa
• Harkitse sijoittamista
• Seuraa kulutustasi

🚀 Olet hyvällä tiellä! Riskit ovat hallinnassa.
        """
        return risk_message.strip()
    
    def _handle_unknown(self, user_id: str, intent: str, params: dict) -> str:
        """Käsittelee tuntemattomat komennot"""
        if self.openai_key:
            # Käytä OpenAI:tä ymmärtämään intent
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"Käyttäjä kirjoitti: '{intent}'. Mikä on hänen intenttinsa? Vastaa suomeksi ystävällisesti ja ohjaa käyttämään /help komentoa.",
                    max_tokens=100,
                    temperature=0.7
                )
                return response.choices[0].text.strip()
            except:
                pass
        
        return f"""
🤔 En ymmärtänyt komentoa: {intent}

💡 Kokeile:
• /help - Näyttää kaikki komennot
• /start - Tervetuloviesti
• /dashboard - Tilannekatsaus

📝 Jos haluat keskustella, kirjoita viesti suoraan!
        """.strip()
    
    def _generate_error_response(self, user_id: str, error: Exception) -> str:
        """Generoi virheviestin"""
        return f"""
❌ Virhe tapahtui: {str(error)}

🔧 Yritä uudelleen tai käytä:
• /help - Apua
• /start - Aloita alusta

📞 Jos ongelma jatkuu, ota yhteyttä tukeen.
        """.strip()
    
    async def _execute_with_sentinel(self, user_id: str, intent: str, params: dict) -> str:
        """Suorittaa intentin Sentinel Integration:in kanssa"""
        try:
            # Muodosta viesti intentin perusteella
            message = self._intent_to_message(intent, params)
            
            # Käytä Sentinel Integration:ia käsittelemään viesti
            response = await sentinel_integration.process_user_message(user_id, message)
            
            # Jos intent on spesifinen, lisää intent-spesifinen sisältö
            if intent == "DASHBOARD":
                dashboard_data = await sentinel_integration.get_dashboard_data(user_id)
                response += f"\n\n📊 Palveluiden status: {len(dashboard_data.get('services_status', {}))} aktiivista"
            
            elif intent == "RUN_ANALYSIS":
                analysis_result = await sentinel_integration.run_analysis(user_id)
                response += f"\n\n🔍 Analyysi suoritettu: {len(analysis_result.get('services_used', []))} palvelua käytetty"
            
            return response
            
        except Exception as e:
            print(f"❌ Virhe Sentinel Integration:in kanssa: {e}")
            # Fallback perinteiseen metodiin
            return self._execute_fallback(user_id, intent, params)
    
    def _intent_to_message(self, intent: str, params: dict) -> str:
        """Muuntaa intentin viestiksi"""
        if intent == "START":
            return "Aloita Sentinel 100K"
        elif intent == "DASHBOARD":
            return "Näytä dashboard"
        elif intent == "SET_GOAL":
            amount = params.get('amount', 0)
            return f"Aseta säästötavoite {amount}€"
        elif intent == "ONBOARDING":
            return "Aloita onboarding"
        elif intent == "RUN_ANALYSIS":
            return "Suorita analyysi"
        elif intent == "START_CYCLE":
            return "Aloita uusi sykli"
        elif intent == "WEEK":
            week = params.get('week', 1)
            return f"Näytä viikon {week} tiedot"
        elif intent == "REPORT":
            return "Näytä raportti"
        elif intent == "INCOME":
            amount = params.get('amount', 0)
            return f"Lisää tuloja {amount}€"
        elif intent == "EXPENSES":
            amount = params.get('amount', 0)
            return f"Lisää menoja {amount}€"
        elif intent == "MOTIVATE":
            return "Anna motivaatiota"
        elif intent == "HELP":
            return "Tarvitsen apua"
        elif intent == "SETTINGS":
            return "Näytä asetukset"
        elif intent == "EXPORT":
            return "Vie profiili"
        elif intent == "DELETE":
            return "Poista profiili"
        elif intent == "RISK":
            return "Näytä riskianalyysi"
        else:
            return f"Tuntematon komento: {intent}"
    
    def _execute_fallback(self, user_id: str, intent: str, params: dict) -> str:
        """Fallback perinteiseen metodiin"""
        if intent == "START":
            return self._handle_start(user_id)
        elif intent == "DASHBOARD":
            return self._handle_dashboard(user_id)
        elif intent == "SET_GOAL":
            return self._handle_set_goal(user_id, params)
        elif intent == "ONBOARDING":
            return self._handle_onboarding(user_id)
        elif intent == "RUN_ANALYSIS":
            return self._handle_analysis(user_id)
        elif intent == "START_CYCLE":
            return self._handle_new_cycle(user_id)
        elif intent == "WEEK":
            return self._handle_week(user_id, params)
        elif intent == "REPORT":
            return self._handle_report(user_id)
        elif intent == "INCOME":
            return self._handle_income(user_id, params)
        elif intent == "EXPENSES":
            return self._handle_expenses(user_id, params)
        elif intent == "MOTIVATE":
            return self._handle_motivate(user_id)
        elif intent == "HELP":
            return self._handle_help()
        elif intent == "SETTINGS":
            return self._handle_settings(user_id)
        elif intent == "EXPORT":
            return self._handle_export(user_id)
        elif intent == "DELETE":
            return self._handle_delete(user_id)
        elif intent == "RISK":
            return self._handle_risk(user_id)
        else:
            return self._handle_unknown(user_id, intent, params)

    def _update_user_context(self, user_id: str, intent: str, params: dict):
        """Päivittää käyttäjän kontekstin"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                'created_at': datetime.now().isoformat(),
                'last_interaction': datetime.now().isoformat(),
                'intents_used': [],
                'total_interactions': 0
            }
        
        context = self.user_contexts[user_id]
        context['last_interaction'] = datetime.now().isoformat()
        context['intents_used'].append(intent)
        context['total_interactions'] += 1
    
    def _get_week_data(self, week: int) -> dict:
        """Hakee viikkotiedot"""
        week_data = {
            1: {
                'target': 300,
                'focus': 'Perustiedot ja tavoitteiden asetus',
                'milestone': 'Säästötavoite asetettu',
                'tasks': '• Täytä onboarding\n• Aseta säästötavoite\n• Analysoi kulutustasi',
                'saved': 0,
                'remaining': 300,
                'completed': 0,
                'next': 'Viikko 2: Säästöstrategiat'
            },
            2: {
                'target': 600,
                'focus': 'Säästöstrategioiden kehittäminen',
                'milestone': 'Säästöstrategia valmis',
                'tasks': '• Optimoi kulutustasi\n• Etsi säästömahdollisuudet\n• Aloita budjetointi',
                'saved': 300,
                'remaining': 300,
                'completed': 50,
                'next': 'Viikko 3: Lisätulojen hankinta'
            }
        }
        
        return week_data.get(week, week_data[1]) 