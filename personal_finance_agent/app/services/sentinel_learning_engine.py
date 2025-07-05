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
        self.status_history = []  # Lisätty statushistoria

class SentinelStatusSystem:
    """Dynaaminen statussysteemi käyttäjälle"""
    
    def __init__(self):
        self.dimensions = {
            'savings_discipline': 0.0,
            'income_growth': 0.0,
            'goal_orientation': 0.0,
            'financial_literacy': 0.0,
            'behavior_change': 0.0
        }
        self.status_history = []
    
    def _analyze_savings_discipline(self, user_id: int, db: Session) -> float:
        """Analysoi säästämisdiscipliinin (0-100%)"""
        try:
            # Hae viimeisen 3 kuukauden transaktiot
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date
            ).all()
            
            if not transactions:
                return 0.0
            
            # Laske säästöt vs kulut
            total_income = sum(t.amount for t in transactions if t.amount > 0)
            total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
            
            if total_income == 0:
                return 0.0
            
            savings_rate = (total_income - total_expenses) / total_income
            
            # Normalisoi 0-100% skaalaan
            return max(0.0, min(100.0, savings_rate * 100))
            
        except Exception as e:
            logger.error(f"Virhe säästämisdiscipliinin analyysissä: {e}")
            return 0.0
    
    def _analyze_income_growth(self, user_id: int, db: Session) -> float:
        """Analysoi tulokasvun (0-100%)"""
        try:
            # Hae viimeisen 6 kuukauden tulot
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0
            ).all()
            
            if not transactions:
                return 0.0
            
            # Ryhmittele kuukausittain
            monthly_income = defaultdict(float)
            for t in transactions:
                month_key = t.transaction_date.strftime('%Y-%m')
                monthly_income[month_key] += t.amount
            
            if len(monthly_income) < 2:
                return 0.0
            
            # Laske kasvutrendi
            months = sorted(monthly_income.keys())
            incomes = [monthly_income[m] for m in months]
            
            if len(incomes) >= 2:
                growth_rate = (incomes[-1] - incomes[0]) / incomes[0] if incomes[0] > 0 else 0
                # Normalisoi 0-100% skaalaan (0% = ei kasvua, 100% = 100% kasvua)
                return max(0.0, min(100.0, growth_rate * 50))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Virhe tulokasvun analyysissä: {e}")
            return 0.0
    
    def _analyze_goal_orientation(self, user_id: int, db: Session) -> float:
        """Analysoi tavoiteorientaation (0-100%)"""
        try:
            # Tämä on yksinkertaistettu versio - oikeassa toteutuksessa
            # käytettäisiin Goal-mallia
            pattern = self.learning_engine.user_patterns.get(user_id)
            if not pattern:
                return 0.0
            
            # Laske tavoiteorientaatio vastausten perusteella
            total_responses = len(pattern.response_patterns)
            goal_responses = sum(1 for r in pattern.response_patterns.values() 
                               if 'goal' in r.get('suggestion_id', '').lower())
            
            if total_responses == 0:
                return 0.0
            
            goal_ratio = goal_responses / total_responses
            return max(0.0, min(100.0, goal_ratio * 100))
            
        except Exception as e:
            logger.error(f"Virhe tavoiteorientaation analyysissä: {e}")
            return 0.0
    
    def _analyze_financial_literacy(self, user_id: int, db: Session) -> float:
        """Analysoi talouslukutaidon (0-100%)"""
        try:
            # Yksinkertaistettu analyysi - oikeassa toteutuksessa
            # käytettäisiin monimutkaisempia mittareita
            
            # Tarkista kategorioiden käyttö
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id
            ).all()
            
            if not transactions:
                return 0.0
            
            # Laske kategorioiden monipuolisuus
            categories = set(t.category for t in transactions if t.category)
            category_diversity = len(categories) / 10  # Normalisoi 10 kategoriaan
            
            # Tarkista budjetin noudattaminen
            pattern = self.learning_engine.user_patterns.get(user_id)
            if pattern:
                effectiveness = np.mean(list(pattern.effectiveness_scores.values())) if pattern.effectiveness_scores else 0
            else:
                effectiveness = 0
            
            # Yhdistä mittarit
            literacy_score = (category_diversity * 50 + effectiveness * 50)
            return max(0.0, min(100.0, literacy_score))
            
        except Exception as e:
            logger.error(f"Virhe talouslukutaidon analyysissä: {e}")
            return 0.0
    
    def _analyze_behavior_change(self, user_id: int, db: Session) -> float:
        """Analysoi käyttäytymismuutoksen (0-100%)"""
        try:
            pattern = self.learning_engine.user_patterns.get(user_id)
            if not pattern:
                return 0.0
            
            # Laske käyttäytymismuutos vastausten perusteella
            total_responses = len(pattern.response_patterns)
            positive_responses = sum(1 for r in pattern.response_patterns.values() 
                                   if r.get('response') in ['accepted', 'partially_followed'])
            
            if total_responses == 0:
                return 0.0
            
            change_ratio = positive_responses / total_responses
            return max(0.0, min(100.0, change_ratio * 100))
            
        except Exception as e:
            logger.error(f"Virhe käyttäytymismuutoksen analyysissä: {e}")
            return 0.0
    
    def _get_savings_status(self, score: float) -> Dict[str, Any]:
        """Hae säästämisdiscipliinin status"""
        if score >= 75:
            return {"title": "💎 Säästölegenda", "description": "Säästät enemmän kuin tarvitsee", "level": 5}
        elif score >= 50:
            return {"title": "🏆 Säästömestari", "description": "Säästät paljon, budjetti optimoitu", "level": 4}
        elif score >= 25:
            return {"title": "💰 Säästäjä", "description": "Säästät säännöllisesti, budjetti hallinnassa", "level": 3}
        elif score >= 10:
            return {"title": "🌱 Säästösiemen", "description": "Aloittaa säästämisen, epäsäännöllisesti", "level": 2}
        else:
            return {"title": "🥶 Kulutusjääti", "description": "Ei säästä mitään, kulut ylittävät tulot", "level": 1}
    
    def _get_income_status(self, score: float) -> Dict[str, Any]:
        """Hae tulokasvun status"""
        if score >= 75:
            return {"title": "💎 Tulolegenda", "description": "Monipuolinen tulopohja, passiiviset tulot", "level": 5}
        elif score >= 50:
            return {"title": "🏢 Yrittäjähenkinen", "description": "Luo uusia tulovirtoja, innovatiivinen", "level": 4}
        elif score >= 25:
            return {"title": "💼 Monitulolainen", "description": "Useita tulovirtoja, aktiivinen", "level": 3}
        elif score >= 10:
            return {"title": "🚀 Tulokasvaja", "description": "Aloittaa lisätulojen etsimisen", "level": 2}
        else:
            return {"title": "😴 Yhden tulon mies", "description": "Vain palkkatulot, ei lisätuloja", "level": 1}
    
    def _get_goal_status(self, score: float) -> Dict[str, Any]:
        """Hae tavoiteorientaation status"""
        if score >= 75:
            return {"title": "💎 Tavoitelegenda", "description": "Ylittää tavoitteet, auttaa muita", "level": 5}
        elif score >= 50:
            return {"title": "🏆 Tavoitemestari", "description": "Saavuttaa tavoitteita, asettaa uusia", "level": 4}
        elif score >= 25:
            return {"title": "📊 Tavoiteseuraaja", "description": "Seuraa edistymistä, päivittää tavoitteita", "level": 3}
        elif score >= 10:
            return {"title": "🎯 Tavoiteetsijä", "description": "Asettaa tavoitteita, ei seuraa", "level": 2}
        else:
            return {"title": "😵 Tavoitehämärä", "description": "Ei tavoitteita, elää päivä kerrallaan", "level": 1}
    
    def _get_literacy_status(self, score: float) -> Dict[str, Any]:
        """Hae talouslukutaidon status"""
        if score >= 75:
            return {"title": "💎 Talouslegenda", "description": "Auttaa muita, luo talousstrategioita", "level": 5}
        elif score >= 50:
            return {"title": "📈 Talousasiantuntija", "description": "Sijoittaa, optimoi verotusta", "level": 4}
        elif score >= 25:
            return {"title": "🧮 Talouslaskija", "description": "Ymmärtää budjetin, tekee päätöksiä", "level": 3}
        elif score >= 10:
            return {"title": "📚 Talousoppilas", "description": "Oppii perusteita, kysyy apua", "level": 2}
        else:
            return {"title": "😵 Taloushämärä", "description": "Ei ymmärrä taloutta, ei budjettia", "level": 1}
    
    def _get_behavior_status(self, score: float) -> Dict[str, Any]:
        """Hae käyttäytymismuutoksen status"""
        if score >= 75:
            return {"title": "💎 Muutoslegenda", "description": "Inspiroi muita, luo uusia tapoja", "level": 5}
        elif score >= 50:
            return {"title": "🏆 Muutosmestari", "description": "Muuttaa käyttäytymistä, auttaa muita", "level": 4}
        elif score >= 25:
            return {"title": "🌱 Muutospuunta", "description": "Muuttaa käyttäytymistä, oppii", "level": 3}
        elif score >= 10:
            return {"title": "🔄 Muutosetsijä", "description": "Yrittää muuttaa, epäonnistuu", "level": 2}
        else:
            return {"title": "😵 Tapojen orja", "description": "Ei muuta käyttäytymistä, vanhat tavat", "level": 1}
    
    def _get_overall_status(self, score: float) -> Dict[str, Any]:
        """Hae yhteisstatuksen"""
        if score >= 80:
            return {"title": "💎 Sentinel Legenda", "description": "Talous-AI:n mestari", "level": 5}
        elif score >= 60:
            return {"title": "🏆 Sentinel Mestari", "description": "Hyvä taloushallinta", "level": 4}
        elif score >= 40:
            return {"title": "💰 Sentinel Säästäjä", "description": "Kehittyvä talousosaaja", "level": 3}
        elif score >= 20:
            return {"title": "🌱 Sentinel Aloittelija", "description": "Oppii taloushallintaa", "level": 2}
        else:
            return {"title": "🥶 Sentinel Uusi", "description": "Aloittaa talousmatkan", "level": 1}
    
    def _get_improvement_areas(self, statuses: Dict) -> List[str]:
        """Hae parannusalueet"""
        improvement_areas = []
        
        for dimension, status in statuses.items():
            if dimension != 'overall_status' and status.get('level', 0) <= 2:
                title = status.get('title', 'Tuntematon')
                improvement_areas.append(f"Paranna {dimension.replace('_', ' ')}: {title}")
        
        return improvement_areas
    
    def _get_next_milestones(self, statuses: Dict) -> List[str]:
        """Hae seuraavat milestonet"""
        milestones = []
        
        for dimension, status in statuses.items():
            if dimension != 'overall_status' and status.get('level', 0) < 5:
                next_level = status.get('level', 0) + 1
                milestones.append(f"Seuraava {dimension.replace('_', ' ')}: Taso {next_level}")
        
        return milestones

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
        self.status_system = SentinelStatusSystem()  # Lisätty statussysteemi
        
        # ML-mallit
        self.expense_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.behavior_clusterer = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        
        # Yhdistä statussysteemi learning engineen
        self.status_system.learning_engine = self
        
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
    
    def get_dynamic_status(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Hae dynaaminen status käyttäjälle"""
        try:
            # Laske 5-dimensionaalinen status
            savings_score = self.status_system._analyze_savings_discipline(user_id, db)
            income_score = self.status_system._analyze_income_growth(user_id, db)
            goal_score = self.status_system._analyze_goal_orientation(user_id, db)
            literacy_score = self.status_system._analyze_financial_literacy(user_id, db)
            behavior_score = self.status_system._analyze_behavior_change(user_id, db)
            
            # Laske yhteispisteet
            overall_score = (savings_score + income_score + goal_score + 
                           literacy_score + behavior_score) / 5
            
            # Hae statukset
            statuses = {
                'savings_status': self.status_system._get_savings_status(savings_score),
                'income_status': self.status_system._get_income_status(income_score),
                'goal_status': self.status_system._get_goal_status(goal_score),
                'literacy_status': self.status_system._get_literacy_status(literacy_score),
                'behavior_status': self.status_system._get_behavior_status(behavior_score),
                'overall_status': self.status_system._get_overall_status(overall_score)
            }
            
            # Tallenna statushistoria
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'dimensions': {
                    'savings_discipline': savings_score,
                    'income_growth': income_score,
                    'goal_orientation': goal_score,
                    'financial_literacy': literacy_score,
                    'behavior_change': behavior_score
                },
                'overall_score': overall_score,
                'statuses': statuses
            }
            
            # Lisää statushistoriaan
            if user_id in self.user_patterns:
                self.user_patterns[user_id].status_history.append(status_data)
            
            return {
                'status': 'success',
                'dimensions': {
                    'savings_discipline': savings_score,
                    'income_growth': income_score,
                    'goal_orientation': goal_score,
                    'financial_literacy': literacy_score,
                    'behavior_change': behavior_score
                },
                'statuses': statuses,
                'overall_score': overall_score,
                'improvement_areas': self.status_system._get_improvement_areas(statuses),
                'next_milestones': self.status_system._get_next_milestones(statuses),
                'status_history': len(self.user_patterns[user_id].status_history) if user_id in self.user_patterns else 0
            }
            
        except Exception as e:
            logger.error(f"Virhe dynaamisen statuksen laskennassa: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'overall_status': self.status_system._get_overall_status(0.0)
            }
    
    def get_status_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Hae statushistoria käyttäjälle"""
        if user_id not in self.user_patterns:
            return []
        
        return self.user_patterns[user_id].status_history
    
    def get_contextual_status(self, user_profile: Dict[str, Any]) -> str:
        """Hae kontekstuaalinen status käyttäjäprofiilin perusteella"""
        try:
            # Alkoholi-ongelma
            if user_profile.get('alcohol_issue', False):
                alcohol_spending = user_profile.get('alcohol_spending', 0)
                if alcohol_spending > 300:
                    return "🍺 Alkoholi-ongelman uhri"
                elif alcohol_spending > 100:
                    return "🍷 Alkoholi-ongelman hallitsija"
                else:
                    return "🥤 Alkoholi-ongelman voittaja"
            
            # Laiskuus
            laziness_level = user_profile.get('laziness_level', 0)
            if laziness_level > 7:
                return "😴 Laiskuuden orja"
            elif laziness_level > 4:
                return "🔄 Laiskuuden voittaja"
            else:
                return "⚡ Aktiivisuuden mestari"
            
            # Talousongelmat
            financial_stress = user_profile.get('financial_stress', 0)
            if financial_stress > 8:
                return "😰 Talousstressin uhri"
            elif financial_stress > 5:
                return "😤 Talousstressin hallitsija"
            else:
                return "😌 Talousrauhan asukas"
            
            # Jos ei mitään sopivaa, palauta oletus
            return "🤔 Status epäselvä"
                
        except Exception as e:
            logger.error(f"Virhe kontekstuaalisen statuksen laskennassa: {e}")
            return "🤔 Status epäselvä" 