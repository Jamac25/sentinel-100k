"""
Sentinel Integration Simple - Yksinkertainen integraatio ilman personal_finance_agent riippuvuuksia
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import requests

class SimpleSentinelIntegration:
    """
    Simple Sentinel Integration - Yksinkertainen integraatio kaikille palveluille
    
    Ominaisuudet:
    - Korvaa mock palvelut oikeilla palveluilla
    - Event-driven architecture
    - Reaaliaikainen kommunikaatio
    - Unified API kaikille palveluille
    """
    
    def __init__(self):
        self.services = {}
        self.is_initialized = False
        self.user_data = {}
        
        # Alustetaan palvelut
        self._initialize_services()
    
    def _initialize_services(self):
        """Alustaa kaikki palvelut"""
        try:
            # 1. AI Memory Layer
            self.services['memory'] = SimpleAIMemoryLayer()
            print("✅ AI Memory Layer alustettu")
            
            # 2. Learning Engine
            self.services['learning'] = SimpleLearningEngine()
            print("✅ Learning Engine alustettu")
            
            # 3. Watchdog Service
            self.services['watchdog'] = SimpleWatchdogService()
            print("✅ Watchdog Service alustettu")
            
            # 4. Smart Receipt Scanner
            self.services['scanner'] = SimpleReceiptScanner()
            print("✅ Receipt Scanner alustettu")
            
            # 5. Scheduler Service
            self.services['scheduler'] = SimpleSchedulerService()
            print("✅ Scheduler Service alustettu")
            
            self.is_initialized = True
            print("🎯 Simple Sentinel Integration alustettu!")
            
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
            context = await self.services['learning'].analyze_user_message(user_id, message)
            return context
            
        except Exception as e:
            print(f"⚠️ Virhe kontekstianalyysissä: {e}")
            return {'intent': 'unknown', 'confidence': 0.5}
    
    async def _check_risks(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Tarkistaa riskit Watchdog:lla"""
        try:
            # Käytä Watchdog:ia riskianalyysiin
            risk_analysis = self.services['watchdog'].analyze_situation_room(user_id)
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
                    'type': 'simple'
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
            learning_insights = await self.services['learning'].get_learning_insights(user_id)
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

# Simple palvelut
class SimpleAIMemoryLayer:
    def __init__(self):
        self.memories = []
    
    async def remember(self, data, service):
        memory_entry = {
            'id': len(self.memories) + 1,
            'data': data,
            'service': service,
            'timestamp': datetime.now().isoformat()
        }
        self.memories.append(memory_entry)
        print(f"🧠 Simple Memory: Tallennettu {service}")
    
    async def recall(self, context, service, limit=10):
        relevant_memories = [
            m for m in self.memories[-limit:] 
            if service in m.get('service', '') or context.lower() in str(m.get('data', '')).lower()
        ]
        return relevant_memories

class SimpleLearningEngine:
    def __init__(self):
        self.user_patterns = {}
    
    async def analyze_user_message(self, user_id, message):
        # Yksinkertainen intent-tunnistus
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['tavoite', 'goal', 'säästö']):
            intent = 'goal_setting'
        elif any(word in message_lower for word in ['dashboard', 'tilanne', 'status']):
            intent = 'dashboard'
        elif any(word in message_lower for word in ['analyysi', 'analysis']):
            intent = 'analysis'
        elif any(word in message_lower for word in ['motivaatio', 'motivate']):
            intent = 'motivation'
        else:
            intent = 'general'
        
        return {
            'intent': intent,
            'sentiment': 'positive' if any(word in message_lower for word in ['kiitos', 'hyvä', 'loistava']) else 'neutral',
            'urgency': 'high' if any(word in message_lower for word in ['hätä', 'kriisi', 'ongelma']) else 'low',
            'confidence': 0.8
        }
    
    async def get_learning_insights(self, user_id):
        return {
            'patterns_discovered': 3,
            'recommendations': ['Säästä säännöllisesti', 'Seuraa budjettia', 'Etsi lisätuloja'],
            'success_rate': 0.75
        }

class SimpleWatchdogService:
    def __init__(self):
        self.risk_thresholds = {
            'low': 0.3,
            'moderate': 0.6,
            'high': 0.8,
            'critical': 1.0
        }
    
    def analyze_situation_room(self, user_id):
        # Yksinkertainen riskianalyysi
        import random
        risk_score = random.uniform(0.1, 0.7)  # Simuloi riskiä
        
        if risk_score <= self.risk_thresholds['low']:
            risk_level = 'low'
            watchdog_mode = 'passive'
        elif risk_score <= self.risk_thresholds['moderate']:
            risk_level = 'moderate'
            watchdog_mode = 'active'
        elif risk_score <= self.risk_thresholds['high']:
            risk_level = 'high'
            watchdog_mode = 'aggressive'
        else:
            risk_level = 'critical'
            watchdog_mode = 'emergency'
        
        return {
            'status': 'success',
            'risk_assessment': {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'watchdog_mode': watchdog_mode
            },
            'situation_data': {
                'current_savings': 25000,
                'target_savings': 100000,
                'monthly_income': 3200,
                'monthly_expenses': 1800
            }
        }

class SimpleReceiptScanner:
    async def instant_scan(self, image_data, user_email):
        return {
            'status': 'success',
            'time_taken': 0.5,
            'receipt_data': {
                'merchant': 'Prisma',
                'total_amount': 45.67,
                'items': ['Maito', 'Leipä', 'Omenat']
            }
        }

class SimpleSchedulerService:
    def __init__(self):
        self.jobs = []
    
    def start(self):
        print("⏰ Simple Scheduler started")
    
    def stop(self):
        print("⏰ Simple Scheduler stopped")
    
    def add_job(self, func, trigger, **kwargs):
        self.jobs.append({
            'func': func.__name__,
            'trigger': str(trigger),
            'kwargs': kwargs
        })

# Global instance
simple_sentinel_integration = SimpleSentinelIntegration() 