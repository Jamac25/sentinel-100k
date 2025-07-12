"""
Sentinel Integration - Integroi kaikki oikeat palvelut ja korvaa mock-versiot
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import requests

# Lisää personal_finance_agent polku
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'personal_finance_agent'))

try:
    from app.services.sentinel_learning_engine import SentinelLearningEngine
    from app.services.sentinel_watchdog_service import SentinelWatchdogService
    from app.services.ai_memory_layer import AIMemoryLayer
    from app.services.smart_receipt_scanner import SmartReceiptScanner
    from app.services.scheduler_service import SchedulerService
    from app.db.init_db import SessionLocal
    print("✅ Kaikki Sentinel-palvelut ladattu!")
except ImportError as e:
    print(f"⚠️ Jotkut palvelut puuttuvat: {e}")
    # Mock-versiot fallbackina
    SentinelLearningEngine = None
    SentinelWatchdogService = None
    AIMemoryLayer = None
    SmartReceiptScanner = None
    SchedulerService = None

class SentinelIntegration:
    """
    Sentinel Integration - Keskitetty integraatio kaikille palveluille
    
    Ominaisuudet:
    - Korvaa mock palvelut oikeilla palveluilla
    - Event-driven architecture
    - Reaaliaikainen kommunikaatio
    - Unified API kaikille palveluille
    """
    
    def __init__(self):
        self.services = {}
        self.is_initialized = False
        self.db_session = None
        
        # Alustetaan palvelut
        self._initialize_services()
    
    def _initialize_services(self):
        """Alustaa kaikki palvelut"""
        try:
            # 1. AI Memory Layer
            if AIMemoryLayer:
                self.services['memory'] = AIMemoryLayer()
                print("✅ AI Memory Layer alustettu")
            else:
                self.services['memory'] = MockAIMemoryLayer()
                print("⚠️ AI Memory Layer - mock versio")
            
            # 2. Learning Engine
            if SentinelLearningEngine:
                self.services['learning'] = SentinelLearningEngine()
                print("✅ Sentinel Learning Engine alustettu")
            else:
                self.services['learning'] = MockLearningEngine()
                print("⚠️ Learning Engine - mock versio")
            
            # 3. Watchdog Service
            if SentinelWatchdogService:
                self.services['watchdog'] = SentinelWatchdogService()
                print("✅ Sentinel Watchdog Service alustettu")
            else:
                self.services['watchdog'] = MockWatchdogService()
                print("⚠️ Watchdog Service - mock versio")
            
            # 4. Smart Receipt Scanner
            if SmartReceiptScanner:
                self.services['scanner'] = SmartReceiptScanner()
                print("✅ Smart Receipt Scanner alustettu")
            else:
                self.services['scanner'] = MockReceiptScanner()
                print("⚠️ Receipt Scanner - mock versio")
            
            # 5. Scheduler Service
            if SchedulerService:
                self.services['scheduler'] = SchedulerService()
                print("✅ Scheduler Service alustettu")
            else:
                self.services['scheduler'] = MockSchedulerService()
                print("⚠️ Scheduler Service - mock versio")
            
            self.is_initialized = True
            print("🎯 Sentinel Integration alustettu!")
            
        except Exception as e:
            print(f"❌ Virhe palveluiden alustuksessa: {e}")
            self.is_initialized = False
    
    async def process_user_message(self, user_id: str, message: str) -> str:
        """
        Käsittelee käyttäjän viestin kaikkien palveluiden kanssa
        
        Args:
            user_id: Käyttäjän ID
            message: Käyttäjän viesti
            
        Returns:
            str: Vastaus käyttäjälle
        """
        if not self.is_initialized:
            return "❌ Palvelut eivät ole alustettu. Yritä uudelleen."
        
        try:
            # 1. Tallenna viesti muistiin
            await self.services['memory'].remember({
                'user_id': user_id,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'type': 'user_message'
            }, 'chat')
            
            # 2. Analysoi viesti Learning Enginellä
            context = await self._analyze_message_context(user_id, message)
            
            # 3. Tarkista riskit Watchdog:lla
            risk_analysis = await self._check_risks(user_id, context)
            
            # 4. Generoi vastaus
            response = await self._generate_response(user_id, message, context, risk_analysis)
            
            # 5. Tallenna vastaus muistiin
            await self.services['memory'].remember({
                'user_id': user_id,
                'response': response,
                'context': context,
                'risk_analysis': risk_analysis,
                'timestamp': datetime.now().isoformat(),
                'type': 'system_response'
            }, 'chat')
            
            return response
            
        except Exception as e:
            print(f"❌ Virhe viestin käsittelyssä: {e}")
            return f"❌ Virhe tapahtui: {str(e)}"
    
    async def _analyze_message_context(self, user_id: str, message: str) -> Dict[str, Any]:
        """Analysoi viestin konteksti Learning Enginellä"""
        try:
            # Käytä Learning Engine:ä analysoimaan viesti
            if hasattr(self.services['learning'], 'analyze_user_message'):
                context = await self.services['learning'].analyze_user_message(user_id, message)
            else:
                # Fallback mock-analyysi
                context = {
                    'intent': 'general',
                    'sentiment': 'neutral',
                    'urgency': 'low',
                    'topics': ['general'],
                    'confidence': 0.8
                }
            
            return context
            
        except Exception as e:
            print(f"⚠️ Virhe kontekstianalyysissä: {e}")
            return {'intent': 'unknown', 'confidence': 0.5}
    
    async def _check_risks(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Tarkistaa riskit Watchdog:lla"""
        try:
            # Käytä Watchdog:ia riskianalyysiin
            if hasattr(self.services['watchdog'], 'analyze_situation_room'):
                # Tarvitaan database session
                if not self.db_session:
                    self.db_session = SessionLocal()
                
                risk_analysis = self.services['watchdog'].analyze_situation_room(
                    int(user_id), self.db_session
                )
            else:
                # Fallback mock-analyysi
                risk_analysis = {
                    'status': 'success',
                    'risk_assessment': {
                        'risk_score': 0.3,
                        'risk_level': 'low',
                        'watchdog_mode': 'passive'
                    }
                }
            
            return risk_analysis
            
        except Exception as e:
            print(f"⚠️ Virhe riskianalyysissä: {e}")
            return {'status': 'error', 'risk_level': 'unknown'}
    
    async def _generate_response(self, user_id: str, message: str, context: Dict[str, Any], risk_analysis: Dict[str, Any]) -> str:
        """Generoi vastauksen kontekstin ja riskianalyysin perusteella"""
        try:
            # Hae relevantit muistit
            memories = await self.services['memory'].recall(message, 'chat', limit=5)
            
            # Muodosta konteksti vastausta varten
            response_context = {
                'user_id': user_id,
                'message': message,
                'context': context,
                'risk_analysis': risk_analysis,
                'memories': memories,
                'timestamp': datetime.now().isoformat()
            }
            
            # Generoi vastaus AI:lla
            if self._has_openai():
                response = await self._generate_ai_response(response_context)
            else:
                response = await self._generate_fallback_response(response_context)
            
            return response
            
        except Exception as e:
            print(f"⚠️ Virhe vastauksen generoinnissa: {e}")
            return "Kiitos viestistäsi! Analysoin tilanteesi ja vastaan pian."
    
    async def _generate_ai_response(self, context: Dict[str, Any]) -> str:
        """Generoi AI-vastaus OpenAI:lla"""
        try:
            import openai
            
            prompt = f"""
Käyttäjä: {context['message']}

Konteksti:
- Intent: {context['context'].get('intent', 'unknown')}
- Riskitaso: {context['risk_analysis'].get('risk_level', 'unknown')}
- Watchdog moodi: {context['risk_analysis'].get('watchdog_mode', 'passive')}

Vastaa suomeksi ystävällisesti ja auttavasti. Ole konkreettinen ja anna käytännön neuvoja.
            """
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].text.strip()
            
        except Exception as e:
            print(f"⚠️ Virhe AI-vastauksessa: {e}")
            return await self._generate_fallback_response(context)
    
    async def _generate_fallback_response(self, context: Dict[str, Any]) -> str:
        """Generoi fallback-vastaus ilman AI:ta"""
        risk_level = context['risk_analysis'].get('risk_level', 'low')
        
        if risk_level == 'high' or risk_level == 'critical':
            return """
⚠️ Huomaan että taloudellinen tilanteesi vaatii huomiota!

💡 Välittömät toimenpiteet:
1. Tarkista kulutustasi tarkasti
2. Etsi säästömahdollisuudet
3. Harkitse lisätulojen hankintaa

🚨 Käytä /analysis saadaksesi yksityiskohtaisen analyysin!
            """.strip()
        else:
            return """
✅ Tilanteesi näyttää hyvältä!

💡 Jatka nykyistä strategiaa:
1. Seuraa budjettiasi
2. Säästä säännöllisesti
3. Etsi lisätulomahdollisuuksia

📊 Käytä /dashboard nähdäksesi tilannekatsauksen!
            """.strip()
    
    def _has_openai(self) -> bool:
        """Tarkistaa onko OpenAI saatavilla"""
        return bool(os.getenv("OPENAI_API_KEY"))
    
    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Hakee dashboard-datan kaikista palveluista"""
        try:
            dashboard_data = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'services_status': {}
            }
            
            # Tarkista palveluiden status
            for service_name, service in self.services.items():
                dashboard_data['services_status'][service_name] = {
                    'status': 'active' if service else 'inactive',
                    'type': 'real' if not service_name.startswith('Mock') else 'mock'
                }
            
            # Lisää riskianalyysi
            risk_analysis = await self._check_risks(user_id, {})
            dashboard_data['risk_analysis'] = risk_analysis
            
            # Lisää muistitiedot
            memories = await self.services['memory'].recall('dashboard', 'chat', limit=3)
            dashboard_data['recent_memories'] = len(memories)
            
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Virhe dashboard-datan haussa: {e}")
            return {'error': str(e)}
    
    async def run_analysis(self, user_id: str) -> Dict[str, Any]:
        """Suorittaa täydellisen analyysin kaikilla palveluilla"""
        try:
            analysis_result = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'services_used': [],
                'findings': []
            }
            
            # 1. Learning Engine analyysi
            if hasattr(self.services['learning'], 'get_learning_insights'):
                learning_insights = self.services['learning'].get_learning_insights(int(user_id))
                analysis_result['findings'].append({
                    'service': 'learning_engine',
                    'insights': learning_insights
                })
                analysis_result['services_used'].append('learning_engine')
            
            # 2. Watchdog analyysi
            risk_analysis = await self._check_risks(user_id, {})
            analysis_result['findings'].append({
                'service': 'watchdog',
                'risk_analysis': risk_analysis
            })
            analysis_result['services_used'].append('watchdog')
            
            # 3. Memory analyysi
            memories = await self.services['memory'].recall('analysis', 'chat', limit=10)
            analysis_result['findings'].append({
                'service': 'memory_layer',
                'memory_count': len(memories),
                'recent_patterns': len([m for m in memories if 'pattern' in m.get('type', '')])
            })
            analysis_result['services_used'].append('memory_layer')
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Virhe analyysin suorittamisessa: {e}")
            return {'error': str(e)}

# Mock palvelut fallbackina
class MockAIMemoryLayer:
    async def remember(self, data, service):
        print(f"🧠 Mock Memory: Tallennettu {service}")
    
    async def recall(self, context, service, limit=10):
        return []

class MockLearningEngine:
    async def analyze_user_message(self, user_id, message):
        return {'intent': 'general', 'confidence': 0.5}

class MockWatchdogService:
    def analyze_situation_room(self, user_id, db):
        return {
            'status': 'success',
            'risk_assessment': {
                'risk_score': 0.3,
                'risk_level': 'low',
                'watchdog_mode': 'passive'
            }
        }

class MockReceiptScanner:
    async def instant_scan(self, image_data, user_email):
        return {'status': 'mock_scan', 'time_taken': 0.1}

class MockSchedulerService:
    def start(self):
        print("⏰ Mock Scheduler started")
    
    def stop(self):
        print("⏰ Mock Scheduler stopped")

# Global instance
sentinel_integration = SentinelIntegration() 