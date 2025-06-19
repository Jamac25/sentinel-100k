"""
Sentinel Learning Engine™ - Kehittynyt oppimismoottori
Tekee Sentinel Watchdog™:sta oppivan AI-kumppanin, joka mukautuu käyttäjään ajan myötä.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.category import Category
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json
import pickle
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class UserBehaviorPattern:
    """Käyttäjän käyttäytymismallin tallentamiseen"""
    
    def __init__(self):
        self.spending_patterns = {}
        self.response_patterns = {}
        self.timing_preferences = {}
        self.communication_style = "balanced"
        self.motivation_triggers = []
        self.effectiveness_scores = defaultdict(float)
        self.learning_rate = 0.1
        
class SentinelLearningEngine:
    """
    Sentinel Learning Engine™ - Kehittynyt oppimismoottori
    
    Oppii käyttäjästä:
    - Kulutuskuviot ja trendit
    - Reagointi ehdotuksiin
    - Optimaalinen kommunikaatiotyyli
    - Motivaatiotekijät
    - Käyttäytymisen ennustaminen
    """
    
    def __init__(self):
        self.user_patterns = {}  # user_id -> UserBehaviorPattern
        self.ml_models = {}      # user_id -> ML models
        self.global_insights = {}
        self.learning_history = defaultdict(list)
        
        # ML-mallit
        self.expense_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.behavior_clusterer = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        
    def initialize_user_learning(self, user_id: int, db: Session) -> UserBehaviorPattern:
        """Alusta käyttäjän oppimisprofiili"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = UserBehaviorPattern()
            
            # Lataa historiallinen data oppimista varten
            self._load_historical_patterns(user_id, db)
            
        return self.user_patterns[user_id]
    
    def _load_historical_patterns(self, user_id: int, db: Session):
        """Lataa historiallinen data oppimisen pohjaksi"""
        try:
            # Hae 6 kuukauden transaktiot
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date
            ).all()
            
            if not transactions:
                logger.info(f"Ei historiallista dataa käyttäjälle {user_id}")
                return
            
            # Analysoi peruskuviot
            self._analyze_spending_patterns(user_id, transactions)
            self._analyze_temporal_patterns(user_id, transactions)
            self._analyze_category_preferences(user_id, transactions)
            
            logger.info(f"Ladattu historiallinen data käyttäjälle {user_id}: {len(transactions)} transaktiota")
            
        except Exception as e:
            logger.error(f"Virhe historiallisen datan latauksessa: {e}")
    
    def _analyze_spending_patterns(self, user_id: int, transactions: List[Transaction]):
        """Analysoi kulutuskuviot"""
        pattern = self.user_patterns[user_id]
        
        # Ryhmittele päivittäin
        daily_spending = defaultdict(float)
        for t in transactions:
            if t.amount > 0:  # Vain kulut
                date_key = t.transaction_date.strftime('%Y-%m-%d')
                daily_spending[date_key] += t.amount
        
        # Laske tilastot
        spending_values = list(daily_spending.values())
        if spending_values:
            pattern.spending_patterns = {
                'daily_avg': statistics.mean(spending_values),
                'daily_std': statistics.stdev(spending_values) if len(spending_values) > 1 else 0,
                'daily_median': statistics.median(spending_values),
                'spending_volatility': statistics.stdev(spending_values) / statistics.mean(spending_values) if statistics.mean(spending_values) > 0 else 0
            }
    
    def _analyze_temporal_patterns(self, user_id: int, transactions: List[Transaction]):
        """Analysoi ajallisia kuvioita"""
        pattern = self.user_patterns[user_id]
        
        # Viikonpäiväanalyysi
        weekday_spending = defaultdict(list)
        hour_spending = defaultdict(list)
        
        for t in transactions:
            if t.amount > 0:
                weekday = t.transaction_date.weekday()  # 0=Monday
                hour = t.transaction_date.hour
                
                weekday_spending[weekday].append(t.amount)
                hour_spending[hour].append(t.amount)
        
        # Laske keskiarvot
        pattern.timing_preferences = {
            'weekday_avg': {day: statistics.mean(amounts) for day, amounts in weekday_spending.items() if amounts},
            'hour_avg': {hour: statistics.mean(amounts) for hour, amounts in hour_spending.items() if amounts},
            'peak_spending_day': max(weekday_spending.items(), key=lambda x: statistics.mean(x[1]) if x[1] else 0)[0] if weekday_spending else 0,
            'peak_spending_hour': max(hour_spending.items(), key=lambda x: statistics.mean(x[1]) if x[1] else 0)[0] if hour_spending else 12
        }
    
    def _analyze_category_preferences(self, user_id: int, transactions: List[Transaction]):
        """Analysoi kategoria-preferenssit"""
        pattern = self.user_patterns[user_id]
        
        category_spending = defaultdict(float)
        category_frequency = defaultdict(int)
        
        for t in transactions:
            if t.amount > 0 and t.category_id:
                category_spending[t.category_id] += t.amount
                category_frequency[t.category_id] += 1
        
        # Tallenna top kategoriat
        pattern.spending_patterns['top_categories'] = dict(
            sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        pattern.spending_patterns['category_frequency'] = dict(category_frequency)
    
    def learn_from_user_response(self, user_id: int, suggestion_id: str, response_type: str, 
                                effectiveness: float = None, db: Session = None):
        """
        Opi käyttäjän vastauksesta ehdotukseen
        
        Args:
            user_id: Käyttäjän ID
            suggestion_id: Ehdotuksen tunniste
            response_type: 'accepted', 'rejected', 'ignored', 'partially_followed'
            effectiveness: 0.0-1.0, kuinka hyvin ehdotus toimi
        """
        pattern = self.initialize_user_learning(user_id, db)
        
        # Tallenna vastaus
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'suggestion_id': suggestion_id,
            'response': response_type,
            'effectiveness': effectiveness
        }
        
        pattern.response_patterns[suggestion_id] = response_data
        
        # Päivitä tehokkuuspisteet
        if effectiveness is not None:
            suggestion_type = suggestion_id.split('_')[0]  # esim. "expense_reduction_food"
            
            # Oppimisalgoritmi: exponential moving average
            current_score = pattern.effectiveness_scores[suggestion_type]
            pattern.effectiveness_scores[suggestion_type] = (
                current_score * (1 - pattern.learning_rate) + 
                effectiveness * pattern.learning_rate
            )
        
        # Mukautu kommunikaatiotyyliin
        self._adapt_communication_style(pattern, response_type, effectiveness)
        
        # Tallenna oppimishistoria
        self.learning_history[user_id].append(response_data)
        
        logger.info(f"Opittu käyttäjältä {user_id}: {response_type} ehdotukseen {suggestion_id}")
    
    def _adapt_communication_style(self, pattern: UserBehaviorPattern, response_type: str, effectiveness: float):
        """Mukaudu kommunikaatiotyyliin käyttäjän vastausten perusteella"""
        
        # Jos käyttäjä hylkii aggressiivisia ehdotuksia
        if response_type == 'rejected' and 'aggressive' in pattern.communication_style:
            pattern.communication_style = 'gentle'
            
        # Jos lempeä tyyli ei toimi, kokeile tiukempaa
        elif response_type == 'ignored' and pattern.communication_style == 'gentle':
            pattern.communication_style = 'firm'
            
        # Jos tehokkuus on korkea, jatka samalla tyylillä
        elif effectiveness and effectiveness > 0.7:
            pass  # Säilytä nykyinen tyyli
            
        # Muuten kokeile tasapainoista lähestymistapaa
        else:
            pattern.communication_style = 'balanced'
    
    def predict_spending(self, user_id: int, days_ahead: int, db: Session) -> Dict[str, Any]:
        """
        Ennusta käyttäjän kulutusta tulevaisuudessa ML:llä
        """
        try:
            pattern = self.initialize_user_learning(user_id, db)
            
            # Hae historiallinen data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0
            ).all()
            
            if len(transactions) < 10:
                return {"status": "insufficient_data", "message": "Ei riittävästi dataa ennustamiseen"}
            
            # Valmistele ominaisuudet (features)
            features = []
            targets = []
            
            # Ryhmittele päivittäin
            daily_data = defaultdict(lambda: {'amount': 0, 'count': 0})
            for t in transactions:
                date_key = t.transaction_date.date()
                daily_data[date_key]['amount'] += t.amount
                daily_data[date_key]['count'] += 1
            
            # Luo aikasarja-ominaisuudet
            sorted_dates = sorted(daily_data.keys())
            for i in range(7, len(sorted_dates)):  # 7 päivän ikkuna
                # Ominaisuudet: edellisten 7 päivän kulutus, viikonpäivä, kuukauden päivä
                date = sorted_dates[i]
                weekday = date.weekday()
                day_of_month = date.day
                
                # Edellisten 7 päivän kulutus
                prev_7_days = [daily_data[sorted_dates[j]]['amount'] for j in range(i-7, i)]
                
                feature_vector = prev_7_days + [weekday, day_of_month]
                features.append(feature_vector)
                targets.append(daily_data[date]['amount'])
            
            if len(features) < 5:
                return {"status": "insufficient_data", "message": "Ei riittävästi dataa mallintamiseen"}
            
            # Skaalaa ominaisuudet
            features_scaled = self.scaler.fit_transform(features)
            
            # Harjoita malli
            self.expense_predictor.fit(features_scaled, targets)
            
            # Tee ennuste
            predictions = []
            last_7_days = [daily_data[sorted_dates[j]]['amount'] for j in range(-7, 0)]
            
            for day in range(days_ahead):
                future_date = end_date.date() + timedelta(days=day+1)
                weekday = future_date.weekday()
                day_of_month = future_date.day
                
                feature_vector = last_7_days + [weekday, day_of_month]
                feature_scaled = self.scaler.transform([feature_vector])
                
                prediction = self.expense_predictor.predict(feature_scaled)[0]
                predictions.append(max(0, prediction))  # Ei negatiivisia ennusteita
                
                # Päivitä liukuvaa ikkunaa
                last_7_days = last_7_days[1:] + [prediction]
            
            return {
                "status": "success",
                "predictions": predictions,
                "total_predicted": sum(predictions),
                "daily_average": sum(predictions) / len(predictions),
                "confidence": "medium",  # Yksinkertainen luottamustaso
                "model_accuracy": self.expense_predictor.score(features_scaled, targets)
            }
            
        except Exception as e:
            logger.error(f"Virhe kulutusennusteessa: {e}")
            return {"status": "error", "message": str(e)}
    
    def detect_spending_anomalies(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Tunnista epätavalliset kulutuskuviot ML:llä
        """
        try:
            pattern = self.initialize_user_learning(user_id, db)
            
            # Hae viimeisen 30 päivän transaktiot
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0
            ).all()
            
            if len(transactions) < 10:
                return []
            
            # Valmistele ominaisuudet anomalian tunnistukseen
            features = []
            transaction_info = []
            
            for t in transactions:
                # Ominaisuudet: summa, viikonpäivä, tunti, kategoria
                weekday = t.transaction_date.weekday()
                hour = t.transaction_date.hour
                category_id = t.category_id or 0
                
                features.append([t.amount, weekday, hour, category_id])
                transaction_info.append({
                    'id': t.id,
                    'amount': t.amount,
                    'date': t.transaction_date.isoformat(),
                    'description': t.description,
                    'category_id': category_id
                })
            
            # Skaalaa ja tunnista anomaliat
            features_scaled = self.scaler.fit_transform(features)
            anomaly_scores = self.anomaly_detector.fit_predict(features_scaled)
            
            # Palauta anomaaliset transaktiot
            anomalies = []
            for i, score in enumerate(anomaly_scores):
                if score == -1:  # Anomalia
                    anomaly_data = transaction_info[i].copy()
                    anomaly_data['anomaly_reason'] = self._explain_anomaly(
                        transaction_info[i], pattern.spending_patterns
                    )
                    anomalies.append(anomaly_data)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Virhe anomalian tunnistuksessa: {e}")
            return []
    
    def _explain_anomaly(self, transaction: Dict, spending_patterns: Dict) -> str:
        """Selitä miksi transaktio on epätavallinen"""
        amount = transaction['amount']
        daily_avg = spending_patterns.get('daily_avg', 0)
        
        if amount > daily_avg * 3:
            return f"Erittäin suuri osto ({amount:.2f}€) verrattuna päivittäiseen keskiarvoon ({daily_avg:.2f}€)"
        elif amount > daily_avg * 2:
            return f"Suuri osto ({amount:.2f}€) verrattuna normaaliin kulutukseen"
        else:
            return "Epätavallinen kulutuskuvio havaittu"
    
    def get_personalized_suggestions(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Luo personoituja ehdotuksia oppimisen perusteella
        """
        pattern = self.initialize_user_learning(user_id, db)
        suggestions = []
        
        # Analysoi tehokkaimmat ehdotustyypit
        effective_types = sorted(
            pattern.effectiveness_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Luo ehdotuksia tehokkaimpien tyyppien perusteella
        for suggestion_type, effectiveness in effective_types[:5]:
            if effectiveness > 0.3:  # Vain kohtuullisen tehokkaat
                suggestion = self._create_personalized_suggestion(
                    suggestion_type, pattern, db
                )
                if suggestion:
                    suggestions.append(suggestion)
        
        # Jos ei ole oppimisdataa, käytä yleisiä ehdotuksia
        if not suggestions:
            suggestions = self._create_general_suggestions(pattern)
        
        return suggestions
    
    def _create_personalized_suggestion(self, suggestion_type: str, pattern: UserBehaviorPattern, db: Session) -> Dict[str, Any]:
        """Luo personoitu ehdotus tyypin perusteella"""
        
        communication_style = pattern.communication_style
        top_categories = pattern.spending_patterns.get('top_categories', {})
        
        if suggestion_type == 'expense_reduction' and top_categories:
            # Ehdota suurimman kategorian optimointia
            top_category_id = max(top_categories.items(), key=lambda x: x[1])[0]
            category = db.query(Category).filter(Category.id == top_category_id).first()
            category_name = category.name if category else "tuntematon kategoria"
            
            return {
                'type': 'expense_reduction',
                'category': category_name,
                'personalization_level': 'high',
                'effectiveness_score': pattern.effectiveness_scores[suggestion_type],
                'message': self._personalize_message(
                    f"Huomasin että kulut {category_name}-kategoriassa ovat suuret. Voisitko optimoida niitä?",
                    communication_style
                ),
                'actions': self._get_category_specific_actions(category_name)
            }
        
        return None
    
    def _personalize_message(self, base_message: str, style: str) -> str:
        """Personoi viesti kommunikaatiotyylin mukaan"""
        
        if style == 'gentle':
            return f"💡 Ehdotus: {base_message} Ei ole pakko, mutta voisi auttaa tavoitteen saavuttamisessa!"
        elif style == 'firm':
            return f"⚠️ Tärkeää: {base_message} Tämä on välttämätöntä tavoitteen saavuttamiseksi."
        elif style == 'aggressive':
            return f"🚨 KRIITTINEN: {base_message.upper()} TOIMENPIDE PAKOLLINEN!"
        else:  # balanced
            return f"🎯 {base_message}"
    
    def _get_category_specific_actions(self, category_name: str) -> List[str]:
        """Hae kategoria-spesifisiä toimenpiteitä"""
        category_lower = category_name.lower()
        
        if "ruoka" in category_lower:
            return [
                "Suunnittele viikon ateriat etukäteen",
                "Kokkaile isompia annoksia ja pakasta",
                "Käytä ruokaostoksissa lista ja budjetti"
            ]
        elif "liikenne" in category_lower:
            return [
                "Kokeile julkisia kulkuneuvoja 2-3 päivää viikossa",
                "Yhdistä asiointimatkoja",
                "Harkitse kimppakyytipalveluja"
            ]
        else:
            return [
                "Arvioi kulujen välttämättömyys",
                "Etsi halvempia vaihtoehtoja",
                "Aseta kuukausittainen kuluraja"
            ]
    
    def _create_general_suggestions(self, pattern: UserBehaviorPattern) -> List[Dict[str, Any]]:
        """Luo yleisiä ehdotuksia kun ei ole oppimisdataa"""
        return [
            {
                'type': 'general',
                'category': 'Aloitus',
                'personalization_level': 'low',
                'message': 'Tervetuloa! Aloitetaan taloudellisen tilanteen kartoituksella.',
                'actions': [
                    'Lisää ensimmäiset transaktiot',
                    'Aseta säästötavoite',
                    'Määritä budjetti kategorioittain'
                ]
            }
        ]
    
    def get_optimal_communication_timing(self, user_id: int) -> Dict[str, Any]:
        """
        Määritä optimaalinen aika kommunikaatiolle käyttäjän kanssa
        """
        if user_id not in self.user_patterns:
            return {
                'best_hour': 18,  # Oletus: iltapäivä
                'best_weekday': 1,  # Oletus: tiistai
                'frequency': 'weekly'
            }
        
        pattern = self.user_patterns[user_id]
        timing_prefs = pattern.timing_preferences
        
        return {
            'best_hour': timing_prefs.get('peak_spending_hour', 18),
            'best_weekday': timing_prefs.get('peak_spending_day', 1),
            'frequency': 'daily' if pattern.communication_style == 'aggressive' else 'weekly',
            'avoid_hours': [0, 1, 2, 3, 4, 5, 6],  # Yöaika
            'preferred_style': pattern.communication_style
        }
    
    def analyze_goal_progress_patterns(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Analysoi tavoitteen edistymiskuvioita ja ennusta onnistumista
        """
        try:
            # Hae historiallinen säästödata
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date
            ).all()
            
            # Laske kuukausittaiset säästöt
            monthly_savings = defaultdict(float)
            for t in transactions:
                month_key = t.transaction_date.strftime('%Y-%m')
                monthly_savings[month_key] += -t.amount if t.amount < 0 else -t.amount
            
            # Analysoi trendi
            savings_values = list(monthly_savings.values())
            if len(savings_values) >= 3:
                # Yksinkertainen lineaarinen trendi
                x = list(range(len(savings_values)))
                trend_slope = np.polyfit(x, savings_values, 1)[0]
                
                # Ennusta 100k€ tavoitteen saavuttaminen
                current_savings = sum(savings_values)
                target = 100000
                remaining = target - current_savings
                
                if trend_slope > 0:
                    months_to_goal = remaining / trend_slope
                    success_probability = min(0.9, max(0.1, 1 - (months_to_goal - 60) / 60))
                else:
                    months_to_goal = float('inf')
                    success_probability = 0.1
                
                return {
                    'current_savings': current_savings,
                    'monthly_trend': trend_slope,
                    'months_to_goal': months_to_goal if months_to_goal != float('inf') else None,
                    'success_probability': success_probability,
                    'recommendation': self._get_goal_recommendation(success_probability, trend_slope)
                }
            
            return {'status': 'insufficient_data'}
            
        except Exception as e:
            logger.error(f"Virhe tavoiteanalyysissä: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_goal_recommendation(self, success_prob: float, trend: float) -> str:
        """Anna suositus tavoitteen perusteella"""
        if success_prob > 0.8:
            return "Erinomaista! Olet erinomaisesti matkalla tavoitteeseen. Jatka samaan malliin!"
        elif success_prob > 0.6:
            return "Hyvää työtä! Pienillä parannuksilla saavutat tavoitteen varmasti."
        elif success_prob > 0.4:
            return "Tarvitset merkittäviä muutoksia säästökäyttäytymiseen tavoitteen saavuttamiseksi."
        else:
            return "Kriittinen tilanne! Radikaalit toimenpiteet ovat välttämättömiä tavoitteen saavuttamiseksi."
    
    def export_learning_data(self, user_id: int) -> Dict[str, Any]:
        """Vie käyttäjän oppimisdata"""
        if user_id not in self.user_patterns:
            return {}
        
        pattern = self.user_patterns[user_id]
        
        return {
            'user_id': user_id,
            'export_timestamp': datetime.now().isoformat(),
            'spending_patterns': pattern.spending_patterns,
            'response_patterns': pattern.response_patterns,
            'timing_preferences': pattern.timing_preferences,
            'communication_style': pattern.communication_style,
            'effectiveness_scores': dict(pattern.effectiveness_scores),
            'learning_history': self.learning_history[user_id]
        }
    
    def import_learning_data(self, learning_data: Dict[str, Any]):
        """Tuo käyttäjän oppimisdata"""
        user_id = learning_data['user_id']
        pattern = UserBehaviorPattern()
        
        pattern.spending_patterns = learning_data.get('spending_patterns', {})
        pattern.response_patterns = learning_data.get('response_patterns', {})
        pattern.timing_preferences = learning_data.get('timing_preferences', {})
        pattern.communication_style = learning_data.get('communication_style', 'balanced')
        pattern.effectiveness_scores = defaultdict(float, learning_data.get('effectiveness_scores', {}))
        
        self.user_patterns[user_id] = pattern
        self.learning_history[user_id] = learning_data.get('learning_history', [])
        
        logger.info(f"Tuotu oppimisdata käyttäjälle {user_id}")
    
    def get_learning_insights(self, user_id: int) -> Dict[str, Any]:
        """Hae oppimisen tulokset ja oivallukset"""
        if user_id not in self.user_patterns:
            return {'status': 'no_data'}
        
        pattern = self.user_patterns[user_id]
        
        # Laske oppimisstatistiikka
        total_interactions = len(self.learning_history[user_id])
        successful_suggestions = sum(1 for h in self.learning_history[user_id] 
                                   if h.get('effectiveness', 0) > 0.5)
        
        success_rate = successful_suggestions / total_interactions if total_interactions > 0 else 0
        
        return {
            'status': 'success',
            'total_interactions': total_interactions,
            'success_rate': success_rate,
            'preferred_communication': pattern.communication_style,
            'most_effective_suggestions': dict(
                sorted(pattern.effectiveness_scores.items(), 
                      key=lambda x: x[1], reverse=True)[:5]
            ),
            'learning_progress': {
                'beginner': total_interactions < 10,
                'intermediate': 10 <= total_interactions < 50,
                'advanced': total_interactions >= 50
            },
            'personalization_level': 'high' if total_interactions > 20 else 'medium' if total_interactions > 5 else 'low'
        } 