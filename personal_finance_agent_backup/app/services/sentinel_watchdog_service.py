"""
Sentinel Watchdog™ - Älykkään käyttäytymismallin mukaan toimiva 100k€ tavoitteen valvoja

Sisältää:
- Tilanneanalyysi (Situation Room -logiikka)
- Toimenpidemoodit (passiivinen/aktiivinen/aggressiivinen/hätätila)
- Motivoiva kommunikaatio (henkilökohtainen valmentaja)
- Autonominen ehdotusmoottori (Goal Survival Engine)
- Hätätila-protokolla
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.category import Category
import logging
import statistics
from enum import Enum

logger = logging.getLogger(__name__)

class WatchdogMode(Enum):
    """Sentinel Watchdog toimenpidemoodit"""
    PASSIVE = "passive"          # 🟢 Valpas seuraaja
    ACTIVE = "active"           # 🟡 Aktiivinen pakottaja  
    AGGRESSIVE = "aggressive"   # 🔴 Panikoiva assistentti
    EMERGENCY = "emergency"     # ⚫ Hätätila

class RiskLevel(Enum):
    """Riskitasot tavoitteen saavuttamiselle"""
    LOW = "low"           # 0.0-0.3
    MODERATE = "moderate" # 0.3-0.6
    HIGH = "high"        # 0.6-0.8
    CRITICAL = "critical" # 0.8-1.0

class SentinelWatchdogService:
    """
    Sentinel Watchdog™ - Älykkään käyttäytymismallin 100k€ valvoja
    
    Toimii kuin henkilökohtainen talousvalmentaja, joka:
    - Analysoi jatkuvasti tilannetta (Situation Room)
    - Vaihtaa toimintamoodia riskitason mukaan
    - Kommunikoi motivoivasti ja konkreettisesti
    - Tekee autonomisia ehdotuksia selviytymiseksi
    - Hälyttää kriittisissä tilanteissa
    """
    
    def __init__(self):
        self.target_amount = 100000  # 100k€ tavoite
        
        # Toimintamoodien kynnysarvot riskipistemäärän mukaan
        self.mode_thresholds = {
            WatchdogMode.PASSIVE: 0.4,      # 0.0-0.4 = passiivinen
            WatchdogMode.ACTIVE: 0.65,      # 0.4-0.65 = aktiivinen
            WatchdogMode.AGGRESSIVE: 0.85,  # 0.65-0.85 = aggressiivinen
            WatchdogMode.EMERGENCY: 1.0     # 0.85-1.0 = hätätila
        }
    
    def analyze_situation_room(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        🧠 Tilanneanalyysi (Situation Room -logiikka)
        
        Laskee jatkuvasti:
        - Todellinen säästötaso vs. tavoitteen vaatima säästövauhti
        - Poikkeamat budjetista ajassa (7pv, 30pv, 90pv)
        - Riskimittari (tulojen volatiliteetti + ennakoidut menot + tavoite-epävarmuus)
        """
        try:
            # Hae käyttäjän tiedot
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"status": "error", "message": "Käyttäjää ei löytynyt"}
            
            # Analysoi eri aikajaksot
            analysis_periods = {"7d": 7, "30d": 30, "90d": 90}
            situation_data = {}
            
            for period_name, days in analysis_periods.items():
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                transactions = db.query(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.transaction_date >= start_date
                ).all()
                
                # Laske tulot ja menot
                income_transactions = [abs(t.amount) for t in transactions if t.amount < 0]
                expense_transactions = [t.amount for t in transactions if t.amount > 0]
                
                total_income = sum(income_transactions)
                total_expenses = sum(expense_transactions)
                net_savings = total_income - total_expenses
                
                # Laske volatiliteetti (tulojen ja kulujen vaihtelevuus)
                income_volatility = statistics.stdev(income_transactions) if len(income_transactions) > 1 else 0
                expense_volatility = statistics.stdev(expense_transactions) if len(expense_transactions) > 1 else 0
                
                situation_data[period_name] = {
                    "total_income": total_income,
                    "total_expenses": total_expenses,
                    "net_savings": net_savings,
                    "daily_savings": net_savings / days if days > 0 else 0,
                    "income_volatility": income_volatility,
                    "expense_volatility": expense_volatility,
                    "transaction_count": len(transactions)
                }
            
            # Laske tavoitteen vaatima säästövauhti
            required_monthly_savings = self.target_amount / (5 * 12)  # 5 vuotta aikaa
            current_monthly_savings = situation_data["30d"]["net_savings"]
            savings_gap = required_monthly_savings - current_monthly_savings
            
            # Laske riskimittari (0.0-1.0)
            risk_score = self._calculate_risk_score(situation_data, savings_gap, required_monthly_savings)
            risk_level = self._determine_risk_level(risk_score)
            watchdog_mode = self._determine_watchdog_mode(risk_score)
            
            return {
                "status": "success",
                "analysis_timestamp": datetime.now().isoformat(),
                "situation_data": situation_data,
                "target_analysis": {
                    "target_amount": self.target_amount,
                    "required_monthly_savings": required_monthly_savings,
                    "current_monthly_savings": current_monthly_savings,
                    "savings_gap": savings_gap,
                    "gap_percentage": (savings_gap / required_monthly_savings) * 100 if required_monthly_savings > 0 else 0
                },
                "risk_assessment": {
                    "risk_score": risk_score,
                    "risk_level": risk_level.value,
                    "watchdog_mode": watchdog_mode.value
                }
            }
            
        except Exception as e:
            logger.error(f"Virhe tilanneanalyysissä: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_risk_score(self, situation_data: Dict, savings_gap: float, required_savings: float) -> float:
        """
        Laske riskimittari (0.0-1.0) joka yhdistää:
        - Säästövaje (40% painoarvo)
        - Tulojen volatiliteetti (25% painoarvo)
        - Kulujen volatiliteetti (20% painoarvo)
        - Trendin suunta (15% painoarvo)
        """
        try:
            # 1. Säästövaje-riski (40% painoarvo)
            if required_savings > 0:
                savings_risk = min(abs(savings_gap) / required_savings, 1.0)
            else:
                savings_risk = 0.0
            
            # 2. Tulojen volatiliteetti-riski (25% painoarvo)
            avg_income = situation_data["30d"]["total_income"] / 30
            income_volatility = situation_data["30d"]["income_volatility"]
            income_risk = min(income_volatility / max(avg_income, 1), 1.0) if avg_income > 0 else 0.5
            
            # 3. Kulujen volatiliteetti-riski (20% painoarvo)
            avg_expenses = situation_data["30d"]["total_expenses"] / 30
            expense_volatility = situation_data["30d"]["expense_volatility"]
            expense_risk = min(expense_volatility / max(avg_expenses, 1), 1.0) if avg_expenses > 0 else 0.5
            
            # 4. Trendin suunta-riski (15% painoarvo)
            # Vertaa 7pv vs 30pv säästöjä
            recent_trend = situation_data["7d"]["daily_savings"]
            monthly_trend = situation_data["30d"]["daily_savings"]
            
            if monthly_trend > 0:
                trend_risk = max(0, (monthly_trend - recent_trend) / monthly_trend)
            else:
                trend_risk = 0.8  # Korkea riski jos ei säästöjä
            
            # Yhdistä painotetusti
            total_risk = (
                savings_risk * 0.40 +
                income_risk * 0.25 +
                expense_risk * 0.20 +
                trend_risk * 0.15
            )
            
            return min(max(total_risk, 0.0), 1.0)  # Varmista 0.0-1.0 välillä
            
        except Exception as e:
            logger.error(f"Virhe riskimittarin laskennassa: {e}")
            return 0.5  # Keskiarvo jos laskenta epäonnistuu
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Määritä riskitaso pistemäärän perusteella"""
        if risk_score <= 0.3:
            return RiskLevel.LOW
        elif risk_score <= 0.6:
            return RiskLevel.MODERATE
        elif risk_score <= 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _determine_watchdog_mode(self, risk_score: float) -> WatchdogMode:
        """Määritä Watchdog-toimintamoodi riskipistemäärän perusteella"""
        if risk_score <= self.mode_thresholds[WatchdogMode.PASSIVE]:
            return WatchdogMode.PASSIVE
        elif risk_score <= self.mode_thresholds[WatchdogMode.ACTIVE]:
            return WatchdogMode.ACTIVE
        elif risk_score <= self.mode_thresholds[WatchdogMode.AGGRESSIVE]:
            return WatchdogMode.AGGRESSIVE
        else:
            return WatchdogMode.EMERGENCY
    
    def get_watchdog_communication(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        🤖 Motivoiva kommunikaatio - Agentti puhuu kuin henkilökohtainen valmentaja
        
        Sentinel ei ainoastaan näytä lukemia. Se puhuu käyttäjän kanssa ja esittää konkreettisia toimia.
        """
        situation = self.analyze_situation_room(user_id, db)
        
        if situation["status"] != "success":
            return situation
        
        watchdog_mode = WatchdogMode(situation["risk_assessment"]["watchdog_mode"])
        savings_gap = situation["target_analysis"]["savings_gap"]
        
        # Valitse kommunikaatiotyyli moodin mukaan
        communication = self._generate_mode_communication(watchdog_mode, savings_gap)
        
        return {
            "status": "success",
            "watchdog_mode": watchdog_mode.value,
            "risk_level": situation["risk_assessment"]["risk_level"],
            "communication": communication,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_mode_communication(self, mode: WatchdogMode, gap: float) -> Dict[str, Any]:
        """Luo kommunikaatio moodin mukaan"""
        
        if mode == WatchdogMode.PASSIVE:
            return {
                "mood": "😊",
                "tone": "encouraging",
                "message": "Hyvää työtä! Olet oikealla tiellä 100k€ tavoitteeseen. Jatka näin!",
                "daily_action": "Tarkista päivän kulut ja nauti onnistumisestasi",
                "weekly_suggestion": "Harkitse kuukausisäästöjen nostamista €50-100 optimoimiseksi",
                "urgency": "none",
                "communication_frequency": "weekly"
            }
        
        elif mode == WatchdogMode.ACTIVE:
            return {
                "mood": "💪",
                "tone": "motivational",
                "message": f"Tarvitsemme {abs(gap):.0f}€/kk lisää tavoitteen saavuttamiseksi. Tässä konkreettiset vaihtoehdot:",
                "daily_action": "Etsi yksi turha kulu tänään ja poista se",
                "weekly_suggestion": "Analysoi suurimmat kuluryhmät ja leikkaa 10-15%",
                "action_plan": [
                    "🔍 Etsi lisätuloja: freelance, sivutyö (+€200-400/kk)",
                    "✂️ Leikkaa kuluja: tilaukset, ravintolat (-€100-200/kk)",
                    "📈 Optimoi sijoitukset: indeksirahastot (5-7% tuotto)"
                ],
                "urgency": "moderate",
                "communication_frequency": "bi-weekly"
            }
        
        elif mode == WatchdogMode.AGGRESSIVE:
            return {
                "mood": "😤",
                "tone": "urgent",
                "message": f"VAROITUS: Tavoite on vakavassa vaarassa! Tarvitsemme {abs(gap):.0f}€/kk HETI. Toimenpiteet välttämättömiä:",
                "daily_action": "PÄIVITTÄINEN TEHTÄVÄ: Lähetä 1 työhakemus tai myy 1 turha tavara",
                "weekly_suggestion": "VIIKOTTAINEN PAKKO: Leikkaa €50 kuluista ja etsi €100 lisätuloja",
                "action_plan": [
                    "🚨 HETI: Rekisteröidy Wolt/Foodora kuljettajaksi",
                    "🚨 TÄNÄÄN: Peruuta kaikki ei-välttämättömät tilaukset",
                    "🚨 VIIKOSSA: Myy käyttämättömät tavarat Tori.fi:ssä",
                    "🚨 KUUKAUDESSA: Neuvottele palkankorotus tai vaihda työpaikkaa"
                ],
                "urgency": "high",
                "communication_frequency": "daily"
            }
        
        else:  # EMERGENCY
            return {
                "mood": "🚨",
                "tone": "emergency",
                "message": "HÄTÄTILA AKTIVOITU! 100k€ tavoite epäonnistuu ilman välittömiä radikaaleja toimia!",
                "daily_action": "KRIITTINEN: Tee vähintään 2 konkreettista toimea päivässä säästöjen lisäämiseksi",
                "weekly_suggestion": "PAKOLLINEN: Toteuta hätäsuunnitelma kokonaisuudessaan",
                "emergency_protocol": {
                    "immediate_actions": [
                        "⚫ TULOT: Aloita kaikki mahdolliset sivutyöt TÄNÄÄN",
                        "⚫ KULUT: Leikkaa KAIKKI ei-välttämättömät menot",
                        "⚫ MYYNTI: Realisoi kaikki turhat omaisuudet",
                        "⚫ ASUMINEN: Harkitse halvempaa asuntoa/kimppakämppää",
                        "⚫ LIIKKUMINEN: Myy auto, käytä julkisia"
                    ],
                    "budget_lockdown": True,
                    "spending_limits": {
                        "entertainment": 0,
                        "dining_out": 0,
                        "shopping": 50,  # Vain välttämätön
                        "transport": 100
                    }
                },
                "urgency": "critical",
                "communication_frequency": "daily_multiple"
            }
    
    def generate_survival_suggestions(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        🔍 Autonominen ehdotusmoottori (Goal Survival Engine)
        
        Analysoi käyttäjän tiedot ja tekee konkreettisia ehdotuksia:
        - Skannaa transaktiot ja löytää säästökohteet
        - Analysoi toistuvia maksuja
        - Ehdottaa lisätulokeinoja
        - Luo konkreettisia toimintasuunnitelmia
        """
        try:
            situation = self.analyze_situation_room(user_id, db)
            if situation["status"] != "success":
                return situation
            
            watchdog_mode = WatchdogMode(situation["risk_assessment"]["watchdog_mode"])
            
            # Hae viimeisen 90 päivän transaktiot kategorisoituna
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0  # Vain kulut
            ).all()
            
            # Analysoi kategorioittain
            category_analysis = {}
            for transaction in transactions:
                category_id = transaction.category_id or 0
                if category_id not in category_analysis:
                    category_analysis[category_id] = {
                        "total": 0,
                        "count": 0,
                        "transactions": []
                    }
                category_analysis[category_id]["total"] += transaction.amount
                category_analysis[category_id]["count"] += 1
                category_analysis[category_id]["transactions"].append(transaction)
            
            suggestions = []
            
            # Kulusäästöehdotukset (top 3 kategoriaa)
            for category_id, data in sorted(category_analysis.items(), key=lambda x: x[1]["total"], reverse=True)[:3]:
                monthly_spend = data["total"] / 3  # 90 päivää -> kuukausi
                if monthly_spend > 100:  # Vain merkittävät kulut
                    category = db.query(Category).filter(Category.id == category_id).first()
                    category_name = category.name if category else f"Kategoria {category_id}"
                    
                    suggestions.append({
                        "type": "expense_reduction",
                        "category": category_name,
                        "current_spend": monthly_spend,
                        "potential_savings": monthly_spend * 0.3,  # 30% säästöpotentiaali
                        "actions": self._get_category_actions(category_name),
                        "urgency": watchdog_mode.value,
                        "estimated_timeline": "2-4 viikkoa"
                    })
            
            # Lisätulo-ehdotukset
            income_suggestions = [
                {
                    "type": "income_increase",
                    "category": "Gig Economy",
                    "potential_income": 300,
                    "actions": [
                        "Rekisteröidy Wolt/Foodora kuljettajaksi",
                        "Aja Uber/Bolt viikonloppuisin",
                        "Tarjoa siivous-/puutarhapalveluja naapurustossa"
                    ],
                    "urgency": watchdog_mode.value,
                    "estimated_timeline": "1 viikko"
                },
                {
                    "type": "income_increase",
                    "category": "Freelance & Konsultointi",
                    "potential_income": 400,
                    "actions": [
                        "Tarjoa osaamistasi Fiverr/Upwork -alustoilla",
                        "Konsultoi omalla alallasi viikonloppuisin",
                        "Opeta taitojasi online-kurssien muodossa"
                    ],
                    "urgency": watchdog_mode.value,
                    "estimated_timeline": "2-4 viikkoa"
                },
                {
                    "type": "income_increase",
                    "category": "Myynti & Kierrätys",
                    "potential_income": 200,
                    "actions": [
                        "Myy käyttämättömät tavarat Tori.fi:ssä",
                        "Kierrätä vaatteet Vinted-palvelussa",
                        "Myy kirjat ja pelit verkossa"
                    ],
                    "urgency": watchdog_mode.value,
                    "estimated_timeline": "1-2 viikkoa"
                }
            ]
            suggestions.extend(income_suggestions)
            
            return {
                "status": "success",
                "analysis_period": "90 days",
                "suggestions": suggestions[:8],  # Top 8 ehdotusta
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Virhe ehdotusmoottorin ajossa: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_category_actions(self, category_name: str) -> List[str]:
        """Luo kategoria-spesifisiä toimintaehdotuksia"""
        category_lower = category_name.lower()
        
        if "ruoka" in category_lower or "ravintola" in category_lower:
            return [
                "Kokkaile kotona 5 päivää viikossa",
                "Käytä ruokaostoksissa budjetti €50/viikko",
                "Lounaalla työpaikkaruokala vs. ravintolat",
                "Valmista isompia annoksia ja pakasta"
            ]
        elif "liikenne" in category_lower or "auto" in category_lower:
            return [
                "Vaihda julkisiin kulkuneuvoihin 3 päivää viikossa",
                "Kimppakyydit työmatkoihin",
                "Pyöräile lyhyet matkat (alle 5km)",
                "Harkitse auton myyntiä jos käyttö vähäistä"
            ]
        elif "viihde" in category_lower or "harrastus" in category_lower:
            return [
                "Peruuta käyttämättömät streaming-palvelut",
                "Vaihda kalliit harrastukset ilmaisiin (kuntosali → ulkoilu)",
                "Käytä kirjastoa viihteen lähteenä",
                "Järjestä kotibileitä ravintolan sijaan"
            ]
        else:
            return [
                "Analysoi kulujen välttämättömyys",
                "Etsi halvempia vaihtoehtoja",
                "Aseta kuukausittainen kuluraja kategoriale"
            ]
    
    def get_emergency_protocol(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        ⚫ Hätätila-protokolla - Kun tavoite on kriittisessä vaarassa
        
        Voi ehdottaa:
        - Budjetin kategorioiden sulkemista
        - Käytön lukitsemista tietyille tileille  
        - Hätäkassastrategiaa
        """
        situation = self.analyze_situation_room(user_id, db)
        
        if situation["status"] != "success":
            return situation
        
        watchdog_mode = WatchdogMode(situation["risk_assessment"]["watchdog_mode"])
        
        if watchdog_mode != WatchdogMode.EMERGENCY:
            return {
                "status": "not_required",
                "message": "Hätätila-protokolla ei ole tarpeen tällä hetkellä",
                "current_mode": watchdog_mode.value
            }
        
        # Luo hätätila-protokolla
        emergency_protocol = {
            "status": "EMERGENCY_ACTIVATED",
            "activation_time": datetime.now().isoformat(),
            "severity": "CRITICAL",
            "immediate_lockdown": {
                "budget_categories_locked": [
                    "viihde", "ravintolat", "vaatteet", "harrastukset", "matkailu"
                ],
                "spending_limits": {
                    "päivittäinen_max": 50,
                    "viikottainen_max": 200,
                    "kuukausittainen_max": 800
                },
                "approval_required_over": 25  # Yli 25€ ostot vaativat vahvistuksen
            },
            "mandatory_actions": [
                {
                    "priority": 1,
                    "action": "TULONLISÄYS PAKOLLINEN",
                    "deadline": "7 päivää",
                    "target": "+€500/kk",
                    "methods": [
                        "Aloita kuljetus-/gig-työt TÄNÄÄN",
                        "Myy kaikki turhat omaisuudet 1 viikossa",
                        "Neuvottele palkankorotus/lisätunnit HETI"
                    ]
                },
                {
                    "priority": 2,
                    "action": "KULUJEN RADIKAALI LEIKKAUS",
                    "deadline": "3 päivää", 
                    "target": "-€400/kk",
                    "methods": [
                        "Peruuta KAIKKI tilaukset (Netflix, Spotify, etc.)",
                        "Syö vain kotona 30 päivää",
                        "Käytä vain julkisia kulkuneuvoja",
                        "Harkitse asunnon vaihtoa halvempaan"
                    ]
                }
            ],
            "communication_protocol": {
                "frequency": "DAILY",
                "channels": ["streamlit", "email", "telegram"],
                "escalation": {
                    "day_3": "Lähetä raportti edistymisestä",
                    "day_7": "Jos ei edistystä → harkitse tavoitteen uudelleenarvointia",
                    "day_14": "Kriittinen arviointi ja uusi strategia"
                }
            },
            "success_metrics": {
                "weekly_savings_increase": 200,
                "monthly_income_increase": 500,
                "expense_reduction": 400
            }
        }
        
        return {
            "status": "success",
            "emergency_protocol": emergency_protocol,
            "estimated_recovery_time": "2-4 viikkoa intensiivistä toimintaa"
        } 