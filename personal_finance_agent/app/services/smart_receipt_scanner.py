"""
SmartReceiptScanner™ - Älykäs kuittiskanneri
Skannaa kuitteja 2 sekunnissa ja integroi kaikkiin AI-palveluihin
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import base64
import io
from PIL import Image
import numpy as np

class SmartReceiptScanner:
    """
    SmartReceiptScanner™ - Älykäs kuittiskanneri
    
    Ominaisuudet:
    - 2 sekunnin skannausaika
    - Automaattinen AI-palveluintegraatio
    - Reaaliaikainen budjettitarkistus
    - Pattern-oppiminen taustalla
    """
    
    def __init__(self):
        self.ocr_engine = MockGoogleVisionAPI()  # Mock toteutus
        self.services = {
            'watchdog': MockSentinelWatchdog(),
            'learning': MockLearningEngine(),
            'ideas': MockIdeaEngine(),
            'chat': MockAIChat(),
            'memory': MockAIMemoryLayer()
        }
        self.scan_history = []
        
    async def instant_scan(self, image_data: bytes, user_email: str = "demo@example.com") -> Dict:
        """
        Skannaa kuitti 2 sekunnissa ja integroi AI-palveluihin
        
        Args:
            image_data: Kuittikuvan data
            user_email: Käyttäjän sähköposti
            
        Returns:
            Dict: Skannauksen tulos
        """
        start_time = time.time()
        
        try:
            # 1. OCR-analyysi (0.5s)
            receipt_data = await self._extract_receipt_data(image_data)
            
            # 2. WATCHDOG: Tarkista budjetti HETI (0.3s)
            budget_check = await self._check_budget_immediately(receipt_data, user_email)
            
            # 3. LEARNING: Opi pattern taustalla (ei vaikuta vastausaikaan)
            asyncio.create_task(
                self._learn_shopping_pattern(receipt_data, user_email)
            )
            
            # 4. IDEAS: Generoi säästöideat jos tarpeen (0.2s)
            savings_ideas = []
            if budget_check.get('budget_warning'):
                savings_ideas = await self._generate_savings_ideas(receipt_data, user_email)
            
            # 5. MEMORY: Tallenna skannaus muistiin (0.1s)
            await self._save_to_memory(receipt_data, budget_check, user_email)
            
            # 6. CHAT: Valmistele vastaus käyttäjälle (0.1s)
            chat_response = await self._prepare_chat_response(receipt_data, budget_check, savings_ideas)
            
            total_time = time.time() - start_time
            
            result = {
                'status': 'success',
                'time_taken': round(total_time, 2),
                'receipt_data': receipt_data,
                'budget_check': budget_check,
                'savings_ideas': savings_ideas,
                'chat_response': chat_response,
                'timestamp': datetime.now().isoformat()
            }
            
            # Tallenna skannaushistoriaan
            self.scan_history.append(result)
            
            print(f"📷 SmartReceiptScanner: Kuitti skannattu {total_time:.2f}s")
            return result
            
        except Exception as e:
            error_time = time.time() - start_time
            print(f"❌ SmartReceiptScanner: Virhe skannauksessa: {e}")
            
            return {
                'status': 'error',
                'error': str(e),
                'time_taken': round(error_time, 2),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _extract_receipt_data(self, image_data: bytes) -> Dict:
        """Poimii kuittidata OCR:llä"""
        # Mock OCR-toteutus - oikeassa toteutuksessa Google Vision API
        receipt_data = {
            'merchant': 'Prisma',
            'total_amount': 45.67,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'items': [
                {'name': 'Maito', 'price': 1.29, 'quantity': 2},
                {'name': 'Leipä', 'price': 2.99, 'quantity': 1},
                {'name': 'Omenat', 'price': 3.49, 'quantity': 1},
                {'name': 'Juusto', 'price': 4.99, 'quantity': 1}
            ],
            'category': 'Ruoka',
            'payment_method': 'Kortti',
            'receipt_id': f"RCPT_{int(time.time())}"
        }
        
        await asyncio.sleep(0.5)  # Simuloi OCR-aikaa
        return receipt_data
    
    async def _check_budget_immediately(self, receipt_data: Dict, user_email: str) -> Dict:
        """Tarkistaa budjetin heti skannauksen jälkeen"""
        amount = receipt_data['total_amount']
        category = receipt_data['category']
        
        # Mock watchdog-tarkistus
        budget_status = await self.services['watchdog'].check_transaction({
            'amount': amount,
            'category': category,
            'user_email': user_email,
            'timestamp': datetime.now().isoformat()
        })
        
        await asyncio.sleep(0.3)  # Simuloi tarkistusaikaa
        
        return {
            'budget_warning': amount > 50,  # Yli 50€ = varoitus
            'category_status': 'within_budget' if amount < 30 else 'approaching_limit',
            'monthly_spent': 1250.50,  # Mock data
            'monthly_budget': 1500.00,
            'remaining_budget': 249.50,
            'suggestions': budget_status.get('suggestions', [])
        }
    
    async def _learn_shopping_pattern(self, receipt_data: Dict, user_email: str) -> None:
        """Oppii ostospatternin taustalla"""
        try:
            learning_data = {
                'user_email': user_email,
                'merchant': receipt_data['merchant'],
                'category': receipt_data['category'],
                'amount': receipt_data['total_amount'],
                'items': receipt_data['items'],
                'timestamp': datetime.now().isoformat(),
                'pattern_type': 'shopping_behavior'
            }
            
            await self.services['learning'].learn_shopping_pattern(learning_data)
            print(f"🧠 SmartReceiptScanner: Oppinut ostospattern {receipt_data['merchant']}")
            
        except Exception as e:
            print(f"⚠️ SmartReceiptScanner: Virhe pattern-oppimisessa: {e}")
    
    async def _generate_savings_ideas(self, receipt_data: Dict, user_email: str) -> List[Dict]:
        """Generoi säästöideat jos budjetti ylitetty"""
        ideas = []
        
        # Analysoi ostokset ja generoi ideat
        expensive_items = [item for item in receipt_data['items'] if item['price'] > 3.0]
        
        if expensive_items:
            for item in expensive_items:
                idea = await self.services['ideas'].generate_quick_income({
                    'context': f"Kallis ostos: {item['name']} ({item['price']}€)",
                    'needed_amount': item['price'],
                    'timeframe': 'this_week',
                    'user_email': user_email
                })
                
                if idea:
                    ideas.append({
                        'type': 'compensation_idea',
                        'item': item['name'],
                        'savings_potential': item['price'],
                        'idea': idea
                    })
        
        await asyncio.sleep(0.2)  # Simuloi idea-generointiaikaa
        return ideas
    
    async def _save_to_memory(self, receipt_data: Dict, budget_check: Dict, user_email: str) -> None:
        """Tallentaa skannauksen AI-muistiin"""
        memory_data = {
            'type': 'receipt_scan',
            'user_email': user_email,
            'receipt_data': receipt_data,
            'budget_check': budget_check,
            'timestamp': datetime.now().isoformat(),
            'service': 'smart_receipt_scanner'
        }
        
        await self.services['memory'].remember(memory_data, 'smart_receipt_scanner')
    
    async def _prepare_chat_response(self, receipt_data: Dict, budget_check: Dict, savings_ideas: List) -> str:
        """Valmistelee chat-vastauksen käyttäjälle"""
        merchant = receipt_data['merchant']
        amount = receipt_data['total_amount']
        
        if budget_check.get('budget_warning'):
            response = f"⚠️ Kuitti tallennettu: {merchant} ({amount}€)\n"
            response += f"Budjettivaroitus: Tämä ostos lähestyy kuukausibudjettia.\n"
            
            if savings_ideas:
                response += f"💡 Säästöidea: {savings_ideas[0]['idea']}"
        else:
            response = f"✅ Kuitti tallennettu: {merchant} ({amount}€)\n"
            response += f"Budjetti: OK - {budget_check['remaining_budget']}€ jäljellä tässä kuussa."
        
        await asyncio.sleep(0.1)  # Simuloi vastausaikaa
        return response
    
    async def get_scan_history(self, user_email: str, limit: int = 10) -> List[Dict]:
        """Hakee skannaushistorian"""
        user_scans = [
            scan for scan in self.scan_history 
            if scan.get('receipt_data', {}).get('user_email') == user_email
        ]
        
        return user_scans[-limit:]
    
    async def analyze_spending_patterns(self, user_email: str) -> Dict:
        """Analysoi käyttäjän ostospatternit"""
        user_scans = await self.get_scan_history(user_email, limit=50)
        
        if not user_scans:
            return {}
        
        # Analysoi kauppoja
        merchants = {}
        categories = {}
        total_spent = 0
        
        for scan in user_scans:
            receipt = scan['receipt_data']
            merchant = receipt['merchant']
            category = receipt['category']
            amount = receipt['total_amount']
            
            merchants[merchant] = merchants.get(merchant, 0) + amount
            categories[category] = categories.get(category, 0) + amount
            total_spent += amount
        
        # Etsi suosikkikauppat
        top_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_scans': len(user_scans),
            'total_spent': total_spent,
            'average_receipt': total_spent / len(user_scans),
            'top_merchants': top_merchants,
            'top_categories': top_categories,
            'scan_frequency': len(user_scans) / 30  # Per kuukausi
        }

# Mock-palvelut testausta varten
class MockGoogleVisionAPI:
    async def extract_receipt(self, image_data):
        return {
            'merchant': 'Test Store',
            'total': 25.50,
            'items': []
        }

class MockSentinelWatchdog:
    async def check_transaction(self, transaction_data):
        return {
            'status': 'ok',
            'suggestions': ['Harkitse halvempaa vaihtoehtoa']
        }

class MockLearningEngine:
    async def learn_shopping_pattern(self, pattern_data):
        return True

class MockIdeaEngine:
    async def generate_quick_income(self, context):
        return "Myy käyttämättömiä tavaroita netissä"

class MockAIChat:
    async def respond(self, message):
        return "Kuitti tallennettu onnistuneesti!"

class MockAIMemoryLayer:
    async def remember(self, data, service):
        return True

# Singleton instance
smart_receipt_scanner = SmartReceiptScanner() 