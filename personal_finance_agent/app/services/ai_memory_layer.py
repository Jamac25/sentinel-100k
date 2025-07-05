"""
AI Memory Layer™ - Semanttinen muisti kaikille AI-palveluille
Tallentaa ja jakaa kontekstin IdeaEngine™, Watchdog™, LearningEngine™ ja Chat-palveluiden kesken
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

class AIMemoryLayer:
    """
    AI Memory Layer™ - Keskitetty muisti kaikille AI-palveluille
    
    Ominaisuudet:
    - Semanttinen muisti kaikille AI-palveluille
    - Automaattinen kontekstin jakaminen
    - Muistin optimointi ja puhdistus
    - Reaaliaikainen oppiminen
    """
    
    def __init__(self):
        self.memory_store = {
            'interactions': [],
            'patterns': {},
            'contexts': {},
            'insights': []
        }
        self.service_memories = {
            'idea_engine': [],
            'watchdog': [],
            'learning_engine': [],
            'chat': [],
            'budget_system': []
        }
        self.memory_index = {}
        
    async def remember(self, interaction: Dict[str, Any], service_name: str) -> str:
        """
        Tallentaa interaktion muistiin ja indeksoi sen
        
        Args:
            interaction: Interaktion data
            service_name: Palvelun nimi joka lähetti interaktion
            
        Returns:
            str: Muistin ID
        """
        memory_id = self._generate_memory_id(interaction)
        
        memory_entry = {
            'id': memory_id,
            'timestamp': datetime.now().isoformat(),
            'service': service_name,
            'data': interaction,
            'context': self._extract_context(interaction),
            'importance': self._calculate_importance(interaction),
            'tags': self._extract_tags(interaction)
        }
        
        # Tallennus päämuistiin
        self.memory_store['interactions'].append(memory_entry)
        
        # Tallennus palvelukohtaiseen muistiin
        if service_name in self.service_memories:
            self.service_memories[service_name].append(memory_entry)
        
        # Indeksointi nopeaa hakua varten
        await self._index_memory(memory_entry)
        
        print(f"🧠 AI Memory Layer: Tallennettu muisti {memory_id} palvelulle {service_name}")
        return memory_id
    
    async def recall(self, context: str, service_name: str, limit: int = 10) -> List[Dict]:
        """
        Hakee relevantin muistin annetulle kontekstille ja palvelulle
        
        Args:
            context: Hakukonteksti
            service_name: Palvelun nimi
            limit: Maksimi määrä tuloksia
            
        Returns:
            List[Dict]: Relevantit muistit
        """
        relevant_memories = []
        
        # Hae palvelukohtaisesta muistista
        if service_name in self.service_memories:
            service_memories = self.service_memories[service_name]
            
            for memory in service_memories:
                relevance_score = self._calculate_relevance(memory, context)
                if relevance_score > 0.3:  # Minimirelevanssi
                    memory['relevance_score'] = relevance_score
                    relevant_memories.append(memory)
        
        # Hae myös yleisestä muistista
        for memory in self.memory_store['interactions']:
            if memory['service'] != service_name:  # Älä toista palvelukohtaista
                relevance_score = self._calculate_relevance(memory, context)
                if relevance_score > 0.5:  # Korkeampi kynnys yleisestä muistista
                    memory['relevance_score'] = relevance_score
                    relevant_memories.append(memory)
        
        # Järjestä relevanssin mukaan ja rajaa määrä
        relevant_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        relevant_memories = relevant_memories[:limit]
        
        print(f"🧠 AI Memory Layer: Haettu {len(relevant_memories)} muistia palvelulle {service_name}")
        return relevant_memories
    
    async def share_context(self, service_name: str, current_context: Dict) -> Dict:
        """
        Jakaa relevantin kontekstin palvelulle
        
        Args:
            service_name: Palvelun nimi
            current_context: Nykyinen konteksti
            
        Returns:
            Dict: Jaettu konteksti
        """
        shared_context = {
            'user_preferences': await self._get_user_preferences(),
            'recent_patterns': await self._get_recent_patterns(service_name),
            'important_insights': await self._get_important_insights(),
            'service_specific': await self._get_service_specific_context(service_name),
            'cross_service_insights': await self._get_cross_service_insights(service_name)
        }
        
        print(f"🧠 AI Memory Layer: Jaettu konteksti palvelulle {service_name}")
        return shared_context
    
    async def learn_pattern(self, pattern_data: Dict, service_name: str) -> None:
        """
        Oppii uuden patternin ja tallentaa sen muistiin
        
        Args:
            pattern_data: Pattern data
            service_name: Palvelun nimi joka oppi patternin
        """
        pattern_id = f"{service_name}_{int(time.time())}"
        
        pattern_entry = {
            'id': pattern_id,
            'service': service_name,
            'pattern': pattern_data,
            'discovered_at': datetime.now().isoformat(),
            'confidence': pattern_data.get('confidence', 0.8),
            'applications': []
        }
        
        self.memory_store['patterns'][pattern_id] = pattern_entry
        
        # Päivitä indeksi
        await self._index_pattern(pattern_entry)
        
        print(f"🧠 AI Memory Layer: Oppinut uusi pattern {pattern_id} palvelulta {service_name}")
    
    async def get_insights(self, service_name: str) -> List[Dict]:
        """
        Hakee insightsejä palvelulle
        
        Args:
            service_name: Palvelun nimi
            
        Returns:
            List[Dict]: Insightit
        """
        insights = []
        
        # Käyttäjän käyttäytymismallit
        behavior_patterns = await self._analyze_behavior_patterns(service_name)
        if behavior_patterns:
            insights.append({
                'type': 'behavior_pattern',
                'data': behavior_patterns,
                'confidence': 0.85
            })
        
        # Taloudelliset trendit
        financial_trends = await self._analyze_financial_trends()
        if financial_trends:
            insights.append({
                'type': 'financial_trend',
                'data': financial_trends,
                'confidence': 0.90
            })
        
        # Optimoimismahdollisuudet
        optimization_opportunities = await self._find_optimization_opportunities(service_name)
        if optimization_opportunities:
            insights.append({
                'type': 'optimization_opportunity',
                'data': optimization_opportunities,
                'confidence': 0.75
            })
        
        print(f"🧠 AI Memory Layer: Generoitu {len(insights)} insighttiä palvelulle {service_name}")
        return insights
    
    def _generate_memory_id(self, interaction: Dict) -> str:
        """Generoi uniikin ID:n interaktiolle"""
        content = json.dumps(interaction, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_context(self, interaction: Dict) -> Dict:
        """Poimii kontekstin interaktiosta"""
        context = {
            'user_id': interaction.get('user_id'),
            'action_type': interaction.get('action_type'),
            'amount': interaction.get('amount'),
            'category': interaction.get('category'),
            'timestamp': interaction.get('timestamp')
        }
        return {k: v for k, v in context.items() if v is not None}
    
    def _calculate_importance(self, interaction: Dict) -> float:
        """Laskee interaktion tärkeyden (0-1)"""
        importance = 0.5  # Oletusarvo
        
        # Suuret summat ovat tärkeämpiä
        if 'amount' in interaction and interaction['amount']:
            amount = abs(float(interaction['amount']))
            if amount > 1000:
                importance += 0.3
            elif amount > 500:
                importance += 0.2
            elif amount > 100:
                importance += 0.1
        
        # Watchdog-hälytykset ovat tärkeitä
        if interaction.get('type') == 'watchdog_alert':
            importance += 0.4
        
        # Ideat ovat tärkeitä
        if interaction.get('type') == 'idea_generated':
            importance += 0.3
        
        return min(importance, 1.0)
    
    def _extract_tags(self, interaction: Dict) -> List[str]:
        """Poimii tagit interaktiosta"""
        tags = []
        
        if 'category' in interaction:
            tags.append(f"category:{interaction['category']}")
        
        if 'action_type' in interaction:
            tags.append(f"action:{interaction['action_type']}")
        
        if 'amount' in interaction:
            amount = abs(float(interaction['amount']))
            if amount > 1000:
                tags.append("high_value")
            elif amount > 500:
                tags.append("medium_value")
            else:
                tags.append("low_value")
        
        return tags
    
    async def _index_memory(self, memory_entry: Dict) -> None:
        """Indeksoi muistin nopeaa hakua varten"""
        memory_id = memory_entry['id']
        
        # Indeksoi tagien mukaan
        for tag in memory_entry.get('tags', []):
            if tag not in self.memory_index:
                self.memory_index[tag] = []
            self.memory_index[tag].append(memory_id)
        
        # Indeksoi palvelun mukaan
        service = memory_entry['service']
        if f"service:{service}" not in self.memory_index:
            self.memory_index[f"service:{service}"] = []
        self.memory_index[f"service:{service}"].append(memory_id)
    
    def _calculate_relevance(self, memory: Dict, context: str) -> float:
        """Laskee muistin relevanssin annetulle kontekstille"""
        relevance = 0.0
        
        # Tarkista tagit
        memory_tags = memory.get('tags', [])
        context_lower = context.lower()
        
        for tag in memory_tags:
            if tag.lower() in context_lower:
                relevance += 0.3
        
        # Tarkista palvelu
        if memory.get('service', '').lower() in context_lower:
            relevance += 0.2
        
        # Tarkista aika (uudemmat ovat relevaantimpia)
        if 'timestamp' in memory:
            try:
                memory_time = datetime.fromisoformat(memory['timestamp'])
                days_old = (datetime.now() - memory_time).days
                if days_old < 7:
                    relevance += 0.2
                elif days_old < 30:
                    relevance += 0.1
            except:
                pass
        
        # Tarkista tärkeys
        relevance += memory.get('importance', 0.5) * 0.3
        
        return min(relevance, 1.0)
    
    async def _get_user_preferences(self) -> Dict:
        """Hakee käyttäjän preferenssit muistista"""
        preferences = {}
        
        # Analysoi käyttäjän käyttäytymistä
        chat_memories = self.service_memories.get('chat', [])
        for memory in chat_memories[-20:]:  # Viimeiset 20
            if 'data' in memory and 'preference' in memory['data']:
                pref_type = memory['data']['preference_type']
                pref_value = memory['data']['preference_value']
                preferences[pref_type] = pref_value
        
        return preferences
    
    async def _get_recent_patterns(self, service_name: str) -> List[Dict]:
        """Hakee viimeaikaiset patternit palvelulle"""
        patterns = []
        
        # Hae palvelukohtaiset patternit
        for pattern_id, pattern in self.memory_store['patterns'].items():
            if pattern['service'] == service_name:
                patterns.append(pattern)
        
        # Järjestä päivämäärän mukaan
        patterns.sort(key=lambda x: x['discovered_at'], reverse=True)
        
        return patterns[:5]  # Viimeiset 5
    
    async def _get_important_insights(self) -> List[Dict]:
        """Hakee tärkeimmät insightit"""
        insights = []
        
        # Hae korkeimman tärkeyden muistit
        high_importance = [
            m for m in self.memory_store['interactions'] 
            if m.get('importance', 0) > 0.8
        ]
        
        for memory in high_importance[-10:]:  # Viimeiset 10
            insights.append({
                'type': 'important_memory',
                'data': memory,
                'source': memory['service']
            })
        
        return insights
    
    async def _get_service_specific_context(self, service_name: str) -> Dict:
        """Hakee palvelukohtaisen kontekstin"""
        context = {}
        
        if service_name in self.service_memories:
            recent_memories = self.service_memories[service_name][-5:]
            
            context['recent_actions'] = [
                {
                    'action': m['data'].get('action_type'),
                    'timestamp': m['timestamp'],
                    'importance': m.get('importance', 0)
                }
                for m in recent_memories
            ]
            
            context['success_rate'] = self._calculate_success_rate(service_name)
            context['user_engagement'] = self._calculate_engagement(service_name)
        
        return context
    
    async def _get_cross_service_insights(self, service_name: str) -> List[Dict]:
        """Hakee insightsejä muista palveluista"""
        cross_insights = []
        
        # Tarkista mitä muut palvelut ovat tehneet
        for other_service, memories in self.service_memories.items():
            if other_service != service_name and memories:
                latest_memory = memories[-1]
                
                cross_insights.append({
                    'service': other_service,
                    'latest_action': latest_memory['data'].get('action_type'),
                    'timestamp': latest_memory['timestamp'],
                    'importance': latest_memory.get('importance', 0)
                })
        
        return cross_insights
    
    async def _analyze_behavior_patterns(self, service_name: str) -> Dict:
        """Analysoi käyttäjän käyttäytymismallit"""
        if service_name not in self.service_memories:
            return {}
        
        memories = self.service_memories[service_name]
        if len(memories) < 5:
            return {}
        
        # Analysoi käyttöaikoja
        usage_times = []
        for memory in memories:
            try:
                time_obj = datetime.fromisoformat(memory['timestamp'])
                usage_times.append(time_obj.hour)
            except:
                continue
        
        if usage_times:
            peak_hour = max(set(usage_times), key=usage_times.count)
            
            return {
                'peak_usage_hour': peak_hour,
                'usage_frequency': len(memories) / 30,  # Per kuukausi
                'engagement_level': 'high' if len(memories) > 20 else 'medium'
            }
        
        return {}
    
    async def _analyze_financial_trends(self) -> Dict:
        """Analysoi taloudellisia trendejä"""
        budget_memories = self.service_memories.get('budget_system', [])
        
        if len(budget_memories) < 10:
            return {}
        
        # Analysoi kulutustrendejä
        expenses = []
        for memory in budget_memories:
            if 'amount' in memory['data'] and memory['data']['amount'] < 0:
                expenses.append(abs(memory['data']['amount']))
        
        if expenses:
            avg_expense = sum(expenses) / len(expenses)
            trend = 'increasing' if expenses[-1] > avg_expense else 'decreasing'
            
            return {
                'average_expense': avg_expense,
                'trend': trend,
                'volatility': self._calculate_volatility(expenses)
            }
        
        return {}
    
    async def _find_optimization_opportunities(self, service_name: str) -> List[Dict]:
        """Etsii optimoimismahdollisuuksia"""
        opportunities = []
        
        # Analysoi käyttäjän käyttäytymistä
        if service_name == 'budget_system':
            # Etsi kategoriat joissa on paljon kulutusta
            category_expenses = {}
            for memory in self.service_memories.get('budget_system', []):
                category = memory['data'].get('category')
                amount = abs(memory['data'].get('amount', 0))
                if category:
                    category_expenses[category] = category_expenses.get(category, 0) + amount
            
            # Etsi korkeimmat kulutuskategoriat
            high_expense_categories = sorted(
                category_expenses.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            for category, amount in high_expense_categories:
                opportunities.append({
                    'type': 'high_expense_category',
                    'category': category,
                    'amount': amount,
                    'suggestion': f'Harkitse kulutusten vähentämistä kategoriassa {category}'
                })
        
        return opportunities
    
    def _calculate_success_rate(self, service_name: str) -> float:
        """Laskee palvelun onnistumisprosentin"""
        memories = self.service_memories.get(service_name, [])
        if not memories:
            return 0.0
        
        successful = sum(1 for m in memories if m['data'].get('success', True))
        return successful / len(memories)
    
    def _calculate_engagement(self, service_name: str) -> str:
        """Laskee käyttäjän sitoutumisen palveluun"""
        memories = self.service_memories.get(service_name, [])
        
        if len(memories) > 50:
            return 'very_high'
        elif len(memories) > 20:
            return 'high'
        elif len(memories) > 10:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Laskee arvojen volatiliteetin"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    async def _index_pattern(self, pattern_entry: Dict) -> None:
        """Indeksoi patternin"""
        pattern_id = pattern_entry['id']
        self.memory_index[f"pattern:{pattern_id}"] = [pattern_id]

# Singleton instance
ai_memory_layer = AIMemoryLayer() 