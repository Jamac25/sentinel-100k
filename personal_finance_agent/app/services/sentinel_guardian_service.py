"""
Sentinel Guardian Service - Aktiivinen 100k€ tavoitteen valvonta
Huutaa käyttäjälle kun tavoite on vaarassa ja ehdottaa radikaaleja toimenpiteitä.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.goal import Goal
from ..models.user import User
import logging

logger = logging.getLogger(__name__)

class SentinelGuardianService:
    """
    Sentinel Guardian - Aktiivinen 100k€ tavoitteen valvonta ja hälytykset.
    Analysoi jatkuvasti käyttäjän taloudellista tilannetta ja huutaa kun tarvitaan toimia.
    """
    
    def __init__(self):
        self.target_amount = 100000  # 100k€ tavoite
        self.critical_threshold = 0.5  # Alle 50% tavoitteesta = kriittinen tilanne
        self.warning_threshold = 0.7   # Alle 70% tavoitteesta = varoitus
        
    def analyze_goal_status(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Analysoi käyttäjän 100k€ tavoitteen tilan ja palauttaa hälytykset.
        """
        try:
            # Hae käyttäjän tiedot
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"status": "error", "message": "Käyttäjää ei löytynyt"}
            
            # Laske nykyinen säästöjen määrä viimeisen 12kk perusteella
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date
            ).all()
            
            # Laske tulot ja menot
            total_income = sum(abs(t.amount) for t in transactions if t.amount < 0)  # Negatiiviset = tulot
            total_expenses = sum(t.amount for t in transactions if t.amount > 0)    # Positiiviset = menot
            monthly_savings = (total_income - total_expenses) / 12
            
            # Arvio nykyisistä säästöistä (tämä tulisi oikeassa toteutuksessa tietokannasta)
            current_savings = max(0, monthly_savings * 12)  # Yksinkertainen arvio
            
            # Laske edistyminen
            progress_percentage = (current_savings / self.target_amount) * 100
            
            # Laske aika tavoitteeseen nykyisellä säästötahdilla
            if monthly_savings > 0:
                remaining_amount = self.target_amount - current_savings
                months_to_goal = remaining_amount / monthly_savings
                realistic_timeline = months_to_goal / 12  # vuosissa
            else:
                months_to_goal = float('inf')
                realistic_timeline = float('inf')
            
            # Analysoi tilanne ja luo hälytykset
            alerts = self._generate_alerts(
                current_savings=current_savings,
                monthly_savings=monthly_savings,
                progress_percentage=progress_percentage,
                realistic_timeline=realistic_timeline,
                total_income=total_income,
                total_expenses=total_expenses
            )
            
            return {
                "status": "success",
                "current_savings": current_savings,
                "monthly_savings": monthly_savings,
                "progress_percentage": progress_percentage,
                "realistic_timeline": realistic_timeline,
                "target_amount": self.target_amount,
                "alerts": alerts,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Virhe tavoiteanalyysissä: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_alerts(self, current_savings: float, monthly_savings: float, 
                        progress_percentage: float, realistic_timeline: float,
                        total_income: float, total_expenses: float) -> List[Dict[str, Any]]:
        """
        Luo hälytykset ja radikaalit toimenpide-ehdotukset tilanteen mukaan.
        """
        alerts = []
        
        # KRIITTINEN TILANNE - Tavoite vaarassa!
        if progress_percentage < 30 or realistic_timeline > 10:
            alerts.extend([
                {
                    "level": "CRITICAL",
                    "title": "🚨 HÄLYTYS: 100K€ TAVOITE VAARASSA!",
                    "message": f"Nykyisellä tahdilla tavoite kestää {realistic_timeline:.1f} vuotta. TOIMIA TARVITAAN NYT!",
                    "actions": [
                        "🔍 ETSI LISÄTÖITÄ HETI - Freelance, sivutoimet, viikonloppuduunit",
                        "💼 NEUVOTTELE PALKANKOROTUS - Varaa tapaaminen pomosi kanssa",
                        "📈 SIJOITA PÖRSSIIN - Aloita kuukausisäästäminen osakkeisiin",
                        "🏠 HARKITSE ASUMISKUSTANNUSTEN PIENENTÄMISTÄ - Kimppakämpät, halvempi alue",
                        "🚗 MYYDÄ AUTO - Julkiset kulkuneuvot säästävät tuhansia",
                        "💡 ALOITA SIVUBISNEKSET - Verkkokauppa, konsultointi, opetus"
                    ],
                    "urgency": "immediate"
                }
            ])
        
        # VAROITUS - Tavoite hidastunut
        elif progress_percentage < 50 or realistic_timeline > 7:
            alerts.extend([
                {
                    "level": "WARNING", 
                    "title": "⚠️ VAROITUS: Säästötahti liian hidas",
                    "message": f"Tavoite kestää {realistic_timeline:.1f} vuotta. Tarvitaan lisätoimia!",
                    "actions": [
                        "💰 NOSTA KUUKAUSISÄÄSTÖJÄ +€200-500",
                        "🔍 ETSI LISÄTULOJA - Osa-aikatyö, freelance",
                        "✂️ LEIKKAA KULUJA - Tarkista tilaukset ja turhat menot",
                        "📈 ALOITA SIJOITTAMINEN - Indeksirahastot tuottavat yli säästötilin",
                        "🎯 ASETA TIUKEMMAT BUDJETTIRAJOITUKSET"
                    ],
                    "urgency": "soon"
                }
            ])
        
        # Spesifiset hälytykset kulujen perusteella
        if total_expenses > total_income * 0.8:  # Yli 80% tuloista menee kuluihin
            alerts.append({
                "level": "WARNING",
                "title": "💸 KULUT LIIAN KORKEAT",
                "message": f"Kulut {total_expenses:.0f}€ ovat {(total_expenses/total_income)*100:.0f}% tuloistasi!",
                "actions": [
                    "🏠 ASUMISKULUT - Suurin yksittäinen säästökohde",
                    "🍽️ RUOKAKULUT - Kotona kokkailu vs. ravintolat", 
                    "🚗 LIIKKUMINEN - Julkiset vs. auto",
                    "📱 TILAUKSET - Peruuta käyttämättömät palvelut",
                    "🛍️ IMPULSSOSTOKSET - 24h harkinta-aika ennen ostoja"
                ],
                "urgency": "moderate"
            })
        
        # Matala säästötaso
        if monthly_savings < 500:
            alerts.append({
                "level": "INFO",
                "title": "📈 SÄÄSTÖJÄ PITÄÄ NOSTAA",
                "message": f"Nykyinen säästö {monthly_savings:.0f}€/kk ei riitä 100k€ tavoitteeseen",
                "actions": [
                    "🎯 TAVOITE: Nosta säästöt vähintään €800/kk",
                    "💼 LISÄTULOT: +€300/kk sivutöistä",
                    "✂️ KULUJEN LEIKKAUS: -€200/kk turhista menoista",
                    "📈 SIJOITUSTUOTTO: 5% vuosituotto kiihdyttää säästöjä"
                ],
                "urgency": "moderate"
            })
        
        # Positiivinen palaute jos menee hyvin
        if progress_percentage > 70 and realistic_timeline < 5:
            alerts.append({
                "level": "SUCCESS",
                "title": "🎉 LOISTAVAA! Olet tavoitteessa",
                "message": f"Nykyisellä tahdilla saavutat 100k€ {realistic_timeline:.1f} vuodessa!",
                "actions": [
                    "💪 JATKA SAMAAN MALLIIN - Säästötahti on erinomainen",
                    "📈 HARKITSE SIJOITTAMISTA - Kiihdytä kasvua osakkeilla",
                    "🎯 ASETA SEURAAVA TAVOITE - 150k€ tai 200k€?",
                    "🏆 JUHLI VÄLITAVOITTEITA - Ansaitset tunnustuksen!"
                ],
                "urgency": "none"
            })
        
        return alerts
    
    def get_daily_motivation(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Päivittäinen motivaatioviesti ja toimenpide-ehdotus.
        """
        analysis = self.analyze_goal_status(user_id, db)
        
        if analysis["status"] != "success":
            return analysis
        
        progress = analysis["progress_percentage"]
        timeline = analysis["realistic_timeline"]
        
        # Valitse päivän viesti tilanteen mukaan
        if progress < 30:
            motivation = {
                "mood": "😤",
                "message": "NOUSE JA PAISTA! 100k€ ei tule itsestään. Tänään etsit lisätöitä!",
                "daily_action": "Lähetä 3 työhakemusta tai ota yhteyttä verkostoosi lisätöiden takia",
                "energy_level": "MAXIMUM"
            }
        elif progress < 50:
            motivation = {
                "mood": "💪", 
                "message": "Tavoite vaatii lisäponnisteluita. Joka päivä on mahdollisuus säästää enemmän!",
                "daily_action": "Tarkista tämän päivän kulut ja kysy itseltäsi: Tarvitsenko tätä?",
                "energy_level": "HIGH"
            }
        elif progress < 70:
            motivation = {
                "mood": "😊",
                "message": "Hyvää vauhtia! Pienet päivittäiset valinnat johtavat suuriin tuloksiin.",
                "daily_action": "Säästä tänään vähintään €10 jättämällä joku ostos tekemättä",
                "energy_level": "STEADY"
            }
        else:
            motivation = {
                "mood": "🚀",
                "message": "Olet tulessa! 100k€ tavoite on saavutettavissa!",
                "daily_action": "Jatka loistavaa työtäsi. Harkitse sijoittamista kasvun kiihdyttämiseksi",
                "energy_level": "CONFIDENT"
            }
        
        return {
            "status": "success",
            "motivation": motivation,
            "progress": progress,
            "days_to_goal": timeline * 365 if timeline != float('inf') else None
        }
    
    def check_spending_anomalies(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Tarkista epätavalliset kulutuspikit ja varoita niistä.
        """
        try:
            # Hae viimeisen 30 päivän transaktiot
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            recent_transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.amount > 0  # Vain kulut
            ).all()
            
            if not recent_transactions:
                return []
            
            # Laske keskimääräinen päivittäinen kulutus
            daily_expenses = {}
            for transaction in recent_transactions:
                date_key = transaction.transaction_date.date()
                if date_key not in daily_expenses:
                    daily_expenses[date_key] = 0
                daily_expenses[date_key] += transaction.amount
            
            if not daily_expenses:
                return []
            
            avg_daily_spending = sum(daily_expenses.values()) / len(daily_expenses)
            
            # Etsi poikkeukselliset päivät (yli 2x keskiarvo)
            anomalies = []
            for date, amount in daily_expenses.items():
                if amount > avg_daily_spending * 2:
                    anomalies.append({
                        "date": date.isoformat(),
                        "amount": amount,
                        "average": avg_daily_spending,
                        "multiplier": amount / avg_daily_spending,
                        "warning": f"🚨 {date.strftime('%d.%m')} kulutit {amount:.0f}€ - {amount/avg_daily_spending:.1f}x normaalia!"
                    })
            
            return sorted(anomalies, key=lambda x: x["multiplier"], reverse=True)
            
        except Exception as e:
            logger.error(f"Virhe kulutusepoikkeusten tarkistuksessa: {e}")
            return []
    
    def generate_emergency_action_plan(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Luo hätätilannetta varten radikaalin toimintasuunnitelman.
        """
        analysis = self.analyze_goal_status(user_id, db)
        
        if analysis["status"] != "success":
            return analysis
        
        current_savings = analysis["current_savings"] 
        monthly_savings = analysis["monthly_savings"]
        timeline = analysis["realistic_timeline"]
        
        # Jos tilanne on kriittinen, luo radikaalit toimenpiteet
        if timeline > 8 or monthly_savings < 300:
            emergency_plan = {
                "status": "EMERGENCY",
                "title": "🚨 HÄTÄTILANNE: 100K€ PELASTUSSUUNNITELMA",
                "immediate_actions": [
                    {
                        "priority": 1,
                        "action": "LISÄTULOT HETI",
                        "details": [
                            "Rekisteröidy Wolt/Foodora kuljettajaksi (aloita tänään)",
                            "Ilmoita freelance-palveluista LinkedInissä",
                            "Myy käyttämättömät tavarat Tori.fi:ssä",
                            "Kysy perheeltä/ystäviltä lyhytaikaisia töitä"
                        ],
                        "target": "+€500/kk lisätuloja"
                    },
                    {
                        "priority": 2, 
                        "action": "KULUJEN RADIKAALI LEIKKAUS",
                        "details": [
                            "Peruuta KAIKKI ei-välttämättömät tilaukset",
                            "Syö kotona 30 päivää (ei ravintoloita)",
                            "Käytä vain julkisia kulkuneuvoja",
                            "Osta vain halvin vaihtoehto kaikesta"
                        ],
                        "target": "-€300/kk kuluja"
                    },
                    {
                        "priority": 3,
                        "action": "SIJOITTAMINEN ALOITETTAVA",
                        "details": [
                            "Avaa sijoitustili Nordeaan/OP:hen",
                            "Aloita €200/kk indeksirahasto-säästäminen", 
                            "Tavoite: 5-7% vuosituotto",
                            "Riskitaso: Keskinkertainen (osakkeet 70%, korot 30%)"
                        ],
                        "target": "Kiihdytä kasvua sijoitustuotoilla"
                    }
                ],
                "timeline_improvement": f"Näillä toimilla tavoite {timeline:.1f} vuodesta → ~5-6 vuoteen",
                "monthly_target": "€800-1000/kk säästöt",
                "success_probability": "85% onnistumistodennäköisyys"
            }
        else:
            emergency_plan = {
                "status": "OPTIMIZATION",
                "title": "⚡ OPTIMOINTISUUNNITELMA",
                "message": "Tilanne ei ole kriittinen, mutta voidaan nopeuttaa tavoitetta"
            }
        
        return emergency_plan 