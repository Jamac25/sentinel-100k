"""
Income Stream Intelligence™ - Tulojen älykkäs analysointi
Analysoi käyttäjän tuloja, tunnistaa epävarmuustekijät ja ehdottaa lisätuloja
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
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class IncomeStream:
    """Yksittäinen tulovirta"""
    
    def __init__(self, source: str, category: str):
        self.source = source
        self.category = category  # salary, freelance, investment, business, other
        self.amounts = []
        self.dates = []
        self.regularity_score = 0.0
        self.trend = 0.0
        self.volatility = 0.0
        self.reliability = "unknown"
        
    def add_transaction(self, amount: float, date: datetime):
        """Lisää tulostapahtuma"""
        self.amounts.append(amount)
        self.dates.append(date)
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Laske tulovirran mittarit"""
        if len(self.amounts) < 2:
            return
            
        # Säännöllisyys (kuinka tasaisin väliajoin tuloja tulee)
        if len(self.dates) >= 3:
            intervals = [(self.dates[i] - self.dates[i-1]).days for i in range(1, len(self.dates))]
            self.regularity_score = 1.0 / (1.0 + statistics.stdev(intervals)) if len(intervals) > 1 else 1.0
        
        # Trendi (kasvava/laskeva)
        if len(self.amounts) >= 3:
            x = list(range(len(self.amounts)))
            self.trend = np.polyfit(x, self.amounts, 1)[0]
        
        # Volatiliteetti
        if len(self.amounts) > 1:
            self.volatility = statistics.stdev(self.amounts) / statistics.mean(self.amounts)
        
        # Luotettavuus
        if self.regularity_score > 0.8 and self.volatility < 0.2:
            self.reliability = "high"
        elif self.regularity_score > 0.5 and self.volatility < 0.4:
            self.reliability = "medium"
        else:
            self.reliability = "low"

class IncomeStreamIntelligence:
    """
    Income Stream Intelligence™ - Tulojen älykkäs analysointi
    
    Analysoi:
    - Tulolähteet ja niiden luotettavuus
    - Tulojen trendit ja volatiliteetti
    - Riskitekijät ja varoitukset
    - Lisätulomahdollisuudet
    """
    
    def __init__(self):
        self.income_streams = {}  # user_id -> List[IncomeStream]
        self.income_suggestions = {
            "freelance": [
                "Graafinen suunnittelu ja logojen teko",
                "Tekstien kirjoittaminen ja käännökset",
                "Verkkosivujen rakentaminen",
                "Valokuvaus ja videointi",
                "Sosiaalisen median hallinta",
                "Online-opetus ja koulutus",
                "Konsultointi omalla alalla"
            ],
            "gig_economy": [
                "Ruoan kotiinkuljetus (Wolt, Foodora)",
                "Taksipalvelut (Uber, Bolt)",
                "Kotisiivous ja kiinteistönhoito",
                "Koiran ulkoilutus ja lemmikkien hoito",
                "Muuttopalvelut ja kuljetus",
                "Kauppa-avustus ja ostospalvelut",
                "Tapahtuma-avustus ja promootio"
            ],
            "passive_income": [
                "Osakkeiden osinkotuotot",
                "P2P-lainaus ja sijoitukset",
                "Vuokra-asunnot ja kiinteistöt",
                "Online-kurssien myynti",
                "Affiliate-markkinointi",
                "Royaltit (kirjat, musiikki, kuvat)",
                "Automatisoitu verkkokauppa"
            ],
            "selling": [
                "Käytettyjen tavaroiden myynti (Tori.fi, Huuto.net)",
                "Käsitöiden ja taiteen myynti",
                "Vintage-vaatteiden kierrätys",
                "Keräilyesineiden myynti",
                "Kotitekoisten tuotteiden myynti",
                "Kirjojen ja pelien myynti",
                "Elektroniikan kierrätys"
            ]
        }
    
    def analyze_income_streams(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Analysoi käyttäjän tulovirrat"""
        try:
            # Hae tulotapahtumat (negatiiviset summat = tulot)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            income_transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount < 0  # Tulot ovat negatiivisia
            ).all()
            
            if not income_transactions:
                return {
                    "status": "no_income_data",
                    "message": "Ei tulotietoja analysoitavaksi",
                    "recommendations": self._get_starter_income_suggestions()
                }
            
            # Ryhmittele tulovirrat
            streams = self._group_income_streams(income_transactions)
            self.income_streams[user_id] = streams
            
            # Analysoi kokonaistilanne
            analysis = self._analyze_overall_income_health(streams)
            
            # Lisää ehdotukset
            analysis["income_suggestions"] = self._generate_income_suggestions(streams, user_id)
            analysis["risk_alerts"] = self._check_income_risks(streams)
            
            return {
                "status": "success",
                "analysis": analysis,
                "income_streams": [self._stream_to_dict(stream) for stream in streams],
                "total_streams": len(streams)
            }
            
        except Exception as e:
            logger.error(f"Virhe tuloanalyysissä: {e}")
            return {"status": "error", "message": str(e)}
    
    def _group_income_streams(self, transactions: List[Transaction]) -> List[IncomeStream]:
        """Ryhmittele transaktiot tulovirroiksi"""
        streams_dict = defaultdict(lambda: defaultdict(list))
        
        for t in transactions:
            # Yritä tunnistaa tulotyyppi kuvauksen perusteella
            income_type = self._classify_income_type(t.description or "")
            source_key = f"{income_type}_{t.description[:20] if t.description else 'unknown'}"
            
            streams_dict[income_type][source_key].append({
                'amount': abs(t.amount),  # Muuta positiiviseksi
                'date': t.transaction_date,
                'description': t.description
            })
        
        # Luo IncomeStream-objektit
        streams = []
        for income_type, sources in streams_dict.items():
            for source_key, transactions in sources.items():
                if len(transactions) >= 2:  # Vähintään 2 tapahtumaa
                    stream = IncomeStream(source_key, income_type)
                    for tx in transactions:
                        stream.add_transaction(tx['amount'], tx['date'])
                    streams.append(stream)
        
        return streams
    
    def _classify_income_type(self, description: str) -> str:
        """Luokittele tulotyyppi kuvauksen perusteella"""
        desc_lower = description.lower()
        
        # Palkka
        if any(word in desc_lower for word in ['palkka', 'salary', 'wage', 'työnantaja']):
            return 'salary'
        
        # Freelance
        if any(word in desc_lower for word in ['lasku', 'invoice', 'freelance', 'konsultointi']):
            return 'freelance'
        
        # Sijoitukset
        if any(word in desc_lower for word in ['osinko', 'dividend', 'korko', 'interest', 'sijoitus']):
            return 'investment'
        
        # Myynti
        if any(word in desc_lower for word in ['myynti', 'sale', 'tori', 'huuto', 'ebay']):
            return 'selling'
        
        # Liiketoiminta
        if any(word in desc_lower for word in ['yritys', 'business', 'firma', 'oy', 'ltd']):
            return 'business'
        
        return 'other'
    
    def _analyze_overall_income_health(self, streams: List[IncomeStream]) -> Dict[str, Any]:
        """Analysoi kokonaistulojen terveydentila"""
        if not streams:
            return {"health_score": 0, "status": "critical"}
        
        total_monthly_income = 0
        reliability_scores = []
        volatility_scores = []
        trend_scores = []
        
        for stream in streams:
            if stream.amounts:
                # Arvioi kuukausitulo
                monthly_estimate = statistics.mean(stream.amounts)
                if stream.regularity_score > 0.5:
                    monthly_estimate *= stream.regularity_score
                
                total_monthly_income += monthly_estimate
                reliability_scores.append(1.0 if stream.reliability == "high" else 0.5 if stream.reliability == "medium" else 0.2)
                volatility_scores.append(max(0, 1.0 - stream.volatility))
                trend_scores.append(max(0, min(1, (stream.trend + 100) / 200)))  # Normalisoi -100 - +100 -> 0-1
        
        # Laske kokonaispistemäärä
        diversity_score = min(1.0, len(streams) / 3)  # Parempi jos useita tulolähteitä
        avg_reliability = statistics.mean(reliability_scores) if reliability_scores else 0
        avg_stability = statistics.mean(volatility_scores) if volatility_scores else 0
        avg_growth = statistics.mean(trend_scores) if trend_scores else 0.5
        
        health_score = (diversity_score * 0.25 + avg_reliability * 0.35 + 
                       avg_stability * 0.25 + avg_growth * 0.15)
        
        # Määritä status
        if health_score > 0.8:
            status = "excellent"
        elif health_score > 0.6:
            status = "good"
        elif health_score > 0.4:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "health_score": health_score,
            "status": status,
            "monthly_income_estimate": total_monthly_income,
            "income_diversity": diversity_score,
            "average_reliability": avg_reliability,
            "income_stability": avg_stability,
            "growth_trend": avg_growth,
            "recommendations": self._get_health_recommendations(health_score, len(streams))
        }
    
    def _generate_income_suggestions(self, streams: List[IncomeStream], user_id: int) -> List[Dict[str, Any]]:
        """Generoi tulonlisäysehdotuksia"""
        suggestions = []
        
        # Analysoi mitä tulolähteitä puuttuu
        existing_types = set(stream.category for stream in streams)
        
        # Ehdota puuttuvia tulotyyppejä
        priority_order = ['freelance', 'gig_economy', 'selling', 'passive_income']
        
        for income_type in priority_order:
            if income_type not in existing_types:
                type_suggestions = self.income_suggestions.get(income_type, [])
                if type_suggestions:
                    suggestions.append({
                        'category': income_type,
                        'type': 'new_income_stream',
                        'priority': 'high' if income_type in ['freelance', 'gig_economy'] else 'medium',
                        'suggestions': type_suggestions[:3],  # Top 3 ehdotusta
                        'estimated_monthly': self._estimate_income_potential(income_type),
                        'difficulty': self._get_difficulty_level(income_type),
                        'time_investment': self._get_time_requirement(income_type)
                    })
        
        # Ehdota olemassa olevien tulovirtojen optimointia
        for stream in streams:
            if stream.reliability == "low" or stream.volatility > 0.5:
                suggestions.append({
                    'category': stream.category,
                    'type': 'optimize_existing',
                    'priority': 'medium',
                    'source': stream.source,
                    'issue': 'low_reliability' if stream.reliability == "low" else 'high_volatility',
                    'optimization_tips': self._get_optimization_tips(stream)
                })
        
        return suggestions[:6]  # Maksimissaan 6 ehdotusta
    
    def _estimate_income_potential(self, income_type: str) -> Dict[str, int]:
        """Arvioi tulotyyppi potentiaali"""
        potentials = {
            'freelance': {'min': 200, 'max': 2000, 'typical': 600},
            'gig_economy': {'min': 100, 'max': 800, 'typical': 300},
            'selling': {'min': 50, 'max': 500, 'typical': 150},
            'passive_income': {'min': 20, 'max': 1000, 'typical': 100}
        }
        return potentials.get(income_type, {'min': 50, 'max': 300, 'typical': 100})
    
    def _get_difficulty_level(self, income_type: str) -> str:
        """Hankaluustaso"""
        levels = {
            'freelance': 'medium',
            'gig_economy': 'easy',
            'selling': 'easy',
            'passive_income': 'hard'
        }
        return levels.get(income_type, 'medium')
    
    def _get_time_requirement(self, income_type: str) -> str:
        """Aikasijoitus"""
        times = {
            'freelance': '5-20h/viikko',
            'gig_economy': '2-15h/viikko',
            'selling': '1-5h/viikko',
            'passive_income': '10-30h aluksi, sitten passiivista'
        }
        return times.get(income_type, '5-10h/viikko')
    
    def _get_optimization_tips(self, stream: IncomeStream) -> List[str]:
        """Optimointiehdotukset olemassa oleville tulovirroille"""
        tips = []
        
        if stream.reliability == "low":
            tips.extend([
                "Pyri säännöllisempiin maksuaikatauluihin",
                "Diversifioi asiakaskuntaa riskin vähentämiseksi",
                "Luo sopimuksia pitkäaikaisemmista yhteistöistä"
            ])
        
        if stream.volatility > 0.5:
            tips.extend([
                "Vakiinnuta hinnoittelu ja palvelupakettisi",
                "Luo ennakoitavia tulomalleja (kuukausimaksut)",
                "Rakenna puskuria tulojen vaihteluille"
            ])
        
        if stream.trend < 0:
            tips.extend([
                "Analysoi miksi tulot laskevat",
                "Päivitä taitojasi ja palvelutarjontaasi",
                "Etsi uusia asiakaskanavia"
            ])
        
        return tips[:3]
    
    def _check_income_risks(self, streams: List[IncomeStream]) -> List[Dict[str, Any]]:
        """Tarkista tuloriskit"""
        risks = []
        
        # Liian riippuvainen yhdestä tulolähteestä
        if len(streams) == 1:
            risks.append({
                'type': 'single_income_dependency',
                'severity': 'high',
                'message': 'Olet riippuvainen vain yhdestä tulolähteestä',
                'recommendation': 'Diversifioi tulojasi lisäämällä uusia tulolähteitä'
            })
        
        # Epäluotettavat tulovirrat
        unreliable_streams = [s for s in streams if s.reliability == "low"]
        if len(unreliable_streams) > len(streams) / 2:
            risks.append({
                'type': 'unreliable_income',
                'severity': 'medium',
                'message': f'{len(unreliable_streams)} tulolähteestä on epäluotettavia',
                'recommendation': 'Vakiinnuta tulolähteitä tai etsi luotettavampia vaihtoehtoja'
            })
        
        # Laskevat tulot
        declining_streams = [s for s in streams if s.trend < -10]
        if declining_streams:
            risks.append({
                'type': 'declining_income',
                'severity': 'high',
                'message': f'{len(declining_streams)} tulolähteen tulot laskevat',
                'recommendation': 'Tutki syitä laskuun ja tee korjaavia toimenpiteitä'
            })
        
        return risks
    
    def _get_health_recommendations(self, health_score: float, stream_count: int) -> List[str]:
        """Terveyssuositukset tulojen perusteella"""
        recommendations = []
        
        if health_score < 0.4:
            recommendations.append("🚨 Kriittinen tilanne: Tulojesi vakaus on heikko")
            recommendations.append("Keskity ensin vakiinnuttamaan nykyiset tulolähteesi")
            recommendations.append("Hae välittömästi lisätuloja gig-taloudesta")
        
        elif health_score < 0.6:
            recommendations.append("⚠️ Tulojesi vakaus voisi olla parempi")
            recommendations.append("Lisää tulolähteiden määrää riskin vähentämiseksi")
            
        if stream_count < 2:
            recommendations.append("Diversifioi tulojasi - yhden tulolähteen varassa oleminen on riskialtista")
        
        if health_score > 0.8:
            recommendations.append("🎉 Erinomaiset tulot! Harkitse passiivisten tulojen lisäämistä")
        
        return recommendations
    
    def _get_starter_income_suggestions(self) -> List[Dict[str, Any]]:
        """Aloittelijaehdotukset kun ei ole tulotietoja"""
        return [
            {
                'category': 'gig_economy',
                'type': 'quick_start',
                'priority': 'high',
                'suggestions': self.income_suggestions['gig_economy'][:3],
                'message': 'Aloita helposti gig-taloudesta'
            },
            {
                'category': 'selling',
                'type': 'immediate',
                'priority': 'high',
                'suggestions': self.income_suggestions['selling'][:3],
                'message': 'Myy tarpeettomia tavaroita välittömästi'
            }
        ]
    
    def _stream_to_dict(self, stream: IncomeStream) -> Dict[str, Any]:
        """Muunna IncomeStream dictionary:ksi"""
        return {
            'source': stream.source,
            'category': stream.category,
            'reliability': stream.reliability,
            'regularity_score': stream.regularity_score,
            'trend': stream.trend,
            'volatility': stream.volatility,
            'transaction_count': len(stream.amounts),
            'average_amount': statistics.mean(stream.amounts) if stream.amounts else 0,
            'total_amount': sum(stream.amounts) if stream.amounts else 0
        }
    
    def get_daily_income_opportunity(self, user_id: int) -> Dict[str, Any]:
        """Hae päivittäinen tulonlisäysmahdollisuus"""
        # Yksinkertainen rotaatio ehdotuksista
        day_of_year = datetime.now().timetuple().tm_yday
        all_suggestions = []
        
        for category, suggestions in self.income_suggestions.items():
            for suggestion in suggestions:
                all_suggestions.append({
                    'category': category,
                    'suggestion': suggestion,
                    'estimated_time': '1-3 tuntia',
                    'potential_earning': f"20-100€"
                })
        
        # Valitse päivän ehdotus
        daily_suggestion = all_suggestions[day_of_year % len(all_suggestions)]
        
        return {
            'status': 'success',
            'daily_opportunity': daily_suggestion,
            'motivational_message': self._get_motivational_message(),
            'action_steps': self._get_action_steps(daily_suggestion['category'])
        }
    
    def _get_motivational_message(self) -> str:
        """Motivoiva viesti"""
        messages = [
            "💪 Jokainen lisäeuro vie sinua lähemmäs 100k€ tavoitetta!",
            "🚀 Tänään on täydellinen päivä aloittaa uusi tulovirta!",
            "💡 Pieni toiminta tänään, suuri muutos tulevaisuudessa!",
            "🎯 100k€ tavoite ei saavuta itseään - aloita tänään!",
            "⭐ Sinussa on potentiaalia ansaita enemmän - hyödynnä se!"
        ]
        
        day_index = datetime.now().timetuple().tm_yday
        return messages[day_index % len(messages)]
    
    def _get_action_steps(self, category: str) -> List[str]:
        """Konkreettiset toimenpiteet kategorialle"""
        steps = {
            'freelance': [
                "Päivitä LinkedIn-profiilisi",
                "Luo portfolio parhaista töistäsi",
                "Rekisteröidy freelance-alustoille"
            ],
            'gig_economy': [
                "Lataa Wolt/Foodora-sovellus",
                "Tarkista ajoneuvosi kunto",
                "Rekisteröidy palveluntarjoajaksi"
            ],
            'selling': [
                "Kierrä koti ja etsi myytäviä tavaroita",
                "Ota hyvät kuvat tuotteista",
                "Luo ilmoitukset Tori.fi:hin"
            ],
            'passive_income': [
                "Tutki sijoitusvaihtoehtoja",
                "Avaa sijoitustili",
                "Aloita pienellä summalla"
            ]
        }
        
        return steps.get(category, ["Aloita tutkimalla mahdollisuuksia", "Tee suunnitelma", "Ota ensimmäinen askel"]) 