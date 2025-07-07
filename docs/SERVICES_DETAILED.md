# 🤖 Sentinel 100K - Palveluiden Tarkka Dokumentaatio

## 📋 Sisällysluettelo

- [Yleiskatsaus](#yleiskatsaus)
- [Authentication Service](#authentication-service)
- [Document Service](#document-service)
- [OCR Service](#ocr-service)
- [Categorization Service](#categorization-service)
- [Transaction Service](#transaction-service)
- [Dashboard Service](#dashboard-service)
- [AI Palvelut](#ai-palvelut)
- [Automaatio](#automaatio)
- [Turvallisuus](#turvallisuus)
- [Käyttöliittymä](#käyttöliittymä)

---

## 🎯 Yleiskatsaus

Sentinel 100K sisältää 16 eri palvelua, jotka kattavat kaikki henkilökohtaisen rahoituksen tarpeet. Jokainen palvelu on modulaarinen ja voidaan käyttää itsenäisesti tai yhdessä muiden palveluiden kanssa.

### 📊 Palveluiden yleiskatsaus
| Palvelu | Tiedosto | Rivit | Tarkoitus |
|---------|----------|-------|-----------|
| AuthService | auth_service.py | 456 | Autentikointi |
| DocumentService | document_service.py | 250 | Dokumenttien käsittely |
| OCRService | ocr_service.py | 212 | Optinen merkkien tunnistus |
| CategorizationService | categorization_service.py | 470 | Kulujen luokittelu |
| TransactionService | transactions.py | 527 | Transaktioiden hallinta |
| DashboardService | dashboard.py | 505 | Taloudellinen yleiskatsaus |
| IdeaEngine | idea_engine.py | 627 | Säästöideat |
| SentinelWatchdog | sentinel_watchdog_service.py | 540 | Seuranta ja hälytykset |
| LearningEngine | sentinel_learning_engine.py | 1012 | Oppiminen |
| CareerIntelligence | career_intelligence.py | 790 | Urakehitys |
| PredictiveBudget | predictive_budget.py | 715 | Budjetin ennustus |
| SchedulerService | scheduler_service.py | 935 | Ajastus |
| EventBus | event_bus.py | 242 | Tapahtumien hallinta |
| FinancialShield | financial_shield.py | 597 | Taloudellinen suoja |
| GuardianService | guardian.py | 366 | Järjestelmän valvonta |
| UserContextService | user_context_service.py | 295 | Käyttäjän konteksti |

---

## 🔐 Authentication Service

**Tiedosto**: `app/services/auth_service.py` (456 riviä)

### Tarkoitus
Käyttäjien turvallinen autentikointi ja hallinta JWT token -pohjaisella järjestelmällä.

### Ominaisuudet
- JWT token generointi ja validointi
- bcrypt salasanan hashaus
- Käyttäjärekisteröityminen ja kirjautuminen
- Token päivitys ja vanhentuminen
- Turvallisuusaudit lokitus
- Salasanan vahvuusvalidointi

### API Endpointit
```python
POST /api/v1/auth/register     # Rekisteröityminen
POST /api/v1/auth/login        # Kirjautuminen
POST /api/v1/auth/refresh      # Token päivitys
GET  /api/v1/auth/me           # Käyttäjätiedot
POST /api/v1/auth/logout       # Kirjautuminen ulos
POST /api/v1/auth/change-password  # Salasanan vaihto
```

### Käyttöesimerkki
```python
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate, UserLogin

# Palvelun alustus
auth_service = AuthService()

# Käyttäjän rekisteröityminen
user_data = UserCreate(
    email="user@example.com",
    name="Test User",
    password="SecurePass123!"
)
user = await auth_service.register_user(user_data)

# Kirjautuminen
login_data = UserLogin(
    email="user@example.com",
    password="SecurePass123!"
)
token = await auth_service.authenticate_user(login_data)

# Token validointi
current_user = await auth_service.get_current_user(token)
```

### Tietokantamalli
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 📄 Document Service

**Tiedosto**: `app/services/document_service.py` (250 riviä)

### Tarkoitus
Kuittien, pankkikorttien ja muiden taloudellisten dokumenttien automaattinen käsittely.

### Ominaisuudet
- Tiedostojen lataus ja validointi
- OCR tekstin tunnistus
- PDF ja kuvatiedostojen käsittely
- Metatietojen tallennus
- Tiedostojen arkistointi
- Tietoturva ja salaus

### API Endpointit
```python
POST /api/v1/documents/upload   # Tiedoston lataus
GET  /api/v1/documents/         # Dokumenttien listaus
GET  /api/v1/documents/{id}     # Dokumentin haku
DELETE /api/v1/documents/{id}   # Dokumentin poisto
POST /api/v1/documents/{id}/process  # Dokumentin käsittely
GET  /api/v1/documents/{id}/text     # Dokumentin teksti
```

### Käyttöesimerkki
```python
from app.services.document_service import DocumentService
from fastapi import UploadFile

# Palvelun alustus
doc_service = DocumentService()

# Dokumentin lataus
with open("receipt.jpg", "rb") as file:
    upload_file = UploadFile(filename="receipt.jpg", file=file)
    document = await doc_service.upload_document(upload_file, user_id=1)

# Tekstin tunnistus
text = await doc_service.extract_text(document.id)

# Dokumentin käsittely
processed_data = await doc_service.process_document(document.id)
```

### Tietokantamalli
```python
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    extracted_text = Column(Text)
    processed_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔍 OCR Service

**Tiedosto**: `app/services/ocr_service.py` (212 riviä)

### Tarkoitus
Optinen merkkien tunnistus (OCR) dokumenteista tekstin poimimiseksi.

### Ominaisuudet
- Tesseract OCR (paikallinen)
- Google Vision API (pilvi)
- Kuvien esikäsittely
- Tekstin puhdistus ja validointi
- Monikielinen tuki
- Suorituskyvyn optimointi

### Käyttöesimerkki
```python
from app.services.ocr_service import TesseractOCRService, GoogleVisionOCRService

# Paikallinen OCR
tesseract_ocr = TesseractOCRService()
text = await tesseract_ocr.extract_text("receipt.jpg")

# Pilvi OCR
google_ocr = GoogleVisionOCRService()
text = await google_ocr.extract_text("receipt.jpg")

# Kuvien esikäsittely
processed_image = await tesseract_ocr.preprocess_image("receipt.jpg")
```

### Konfiguraatio
```python
# app/core/config.py
OCR_SERVICE = "tesseract"  # tai "google_vision"
TESSERACT_PATH = "/usr/bin/tesseract"
GOOGLE_CREDENTIALS = "path/to/credentials.json"
```

---

## 🏷️ Categorization Service

**Tiedosto**: `app/services/categorization_service.py` (470 riviä)

### Tarkoitus
Kulujen automaattinen luokittelu koneoppimisen avulla.

### Ominaisuudet
- ML-pohjainen luokittelu
- Käyttäjän korjaukset oppimiseen
- Säännönpohjainen luokittelu
- Kategorioiden hallinta
- Tilastot ja raportointi
- Suorituskyvyn seuranta

### API Endpointit
```python
POST /api/v1/categories/predict    # Kategorian ennustus
PUT  /api/v1/categories/correct    # Korjaus
GET  /api/v1/categories/stats      # Tilastot
GET  /api/v1/categories/usage      # Käyttötilastot
POST /api/v1/categories/train      # Mallin koulutus
```

### Käyttöesimerkki
```python
from app.services.categorization_service import TransactionCategorizationService

# Palvelun alustus
cat_service = TransactionCategorizationService()

# Kategorian ennustus
category = await cat_service.predict_category(
    description="K-Market ruokaostokset",
    amount=45.67
)

# Korjaus oppimiseen
await cat_service.correct_categorization(
    transaction_id=123,
    new_category="ruoka",
    confidence=0.95
)

# Tilastot
stats = await cat_service.get_categorization_stats(user_id=1)
```

### ML-malli
```python
class CategorizationModel:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('classifier', RandomForestClassifier())
        ])
        self.categories = [
            'ruoka', 'kuljetus', 'viihde', 'terveys',
            'asuminen', 'vaatteet', 'koulutus', 'muu'
        ]
```

---

## 💰 Transaction Service

**Tiedosto**: `app/api/transactions.py` (527 riviä)

### Tarkoitus
Kulujen ja tulojen kattava hallinta ja analysointi.

### Ominaisuudet
- Transaktioiden CRUD operaatiot
- Automaattinen kategorointi
- Summien laskenta
- Filtteröinti ja hakutoiminnot
- Bulk operaatiot
- Tilastot ja raportointi

### API Endpointit
```python
POST /api/v1/transactions/         # Uusi transaktio
GET  /api/v1/transactions/         # Transaktioiden listaus
PUT  /api/v1/transactions/{id}     # Transaktion päivitys
DELETE /api/v1/transactions/{id}   # Transaktion poisto
GET  /api/v1/transactions/stats    # Tilastot
POST /api/v1/transactions/bulk     # Bulk operaatiot
GET  /api/v1/transactions/search   # Hakutoiminnot
```

### Käyttöesimerkki
```python
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate

# Palvelun alustus
tx_service = TransactionService()

# Uusi transaktio
transaction_data = TransactionCreate(
    description="K-Market ruokaostokset",
    amount=45.67,
    category="ruoka",
    date="2024-01-15"
)
transaction = await tx_service.create_transaction(transaction_data, user_id=1)

# Transaktioiden haku
transactions = await tx_service.get_transactions(
    user_id=1,
    start_date="2024-01-01",
    end_date="2024-01-31",
    category="ruoka"
)

# Tilastot
stats = await tx_service.get_transaction_stats(user_id=1)
```

### Tietokantamalli
```python
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    amount = Column(Decimal)
    category = Column(String)
    date = Column(Date)
    type = Column(String, default="expense")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 📊 Dashboard Service

**Tiedosto**: `app/api/dashboard.py` (505 riviä)

### Tarkoitus
Taloudellinen yleiskatsaus ja analytiikka reaaliajassa.

### Ominaisuudet
- Reaaliaikainen saldo
- Kulujen trendit
- Säästöjen seuranta
- Kategorioiden jakauma
- Tavoitteiden eteneminen
- Interaktiiviset kaaviot

### API Endpointit
```python
GET /api/v1/dashboard/summary      # Yhteenveto
GET /api/v1/dashboard/insights     # Oivallukset
GET /api/v1/dashboard/charts       # Kaaviot
GET /api/v1/dashboard/goals        # Tavoitteet
GET /api/v1/dashboard/trends       # Trendit
GET /api/v1/dashboard/alerts       # Hälytykset
```

### Käyttöesimerkki
```python
from app.services.dashboard_service import DashboardService

# Palvelun alustus
dashboard_service = DashboardService()

# Yhteenveto
summary = await dashboard_service.get_summary(user_id=1)

# Oivallukset
insights = await dashboard_service.get_insights(user_id=1)

# Kaaviot
charts = await dashboard_service.get_charts(user_id=1)

# Tavoitteet
goals = await dashboard_service.get_goals_progress(user_id=1)
```

### Yhteenveto-rakenne
```python
class DashboardSummary:
    total_balance: float
    monthly_income: float
    monthly_expenses: float
    savings_rate: float
    goal_progress: float
    top_categories: List[CategoryStats]
    recent_transactions: List[Transaction]
    alerts: List[Alert]
```

---

## 🤖 AI Palvelut

### 7.1 IdeaEngine™
**Tiedosto**: `app/services/idea_engine.py` (627 riviä)

**Tarkoitus**: Säästöideoiden generointi

**Ominaisuudet**:
- AI-pohjaiset säästövinkit
- Henkilökohtaiset suositukset
- Kontekstipohjainen neuvonta
- Ideoiden arviointi
- Säästöpotentiaalin laskenta
- Ideoiden seuranta

**API Endpointit**:
```python
POST /api/v1/ideas/generate
GET  /api/v1/ideas/
GET  /api/v1/ideas/{id}
POST /api/v1/ideas/{id}/implement
GET  /api/v1/ideas/savings-potential
```

### 7.2 SentinelWatchdog™
**Tiedosto**: `app/services/sentinel_watchdog_service.py` (540 riviä)

**Tarkoitus**: Reaaliaikainen seuranta ja hälytykset

**Ominaisuudet**:
- Kulutrendien seuranta
- Anomalian tunnistus
- Automaattiset hälytykset
- Proaktiivinen neuvonta
- Riskien arviointi
- Hälytysten hallinta

**API Endpointit**:
```python
GET /api/v1/watchdog/status
GET /api/v1/watchdog/alerts
POST /api/v1/watchdog/acknowledge/{alert_id}
GET /api/v1/watchdog/analytics
POST /api/v1/watchdog/configure
```

### 7.3 LearningEngine™
**Tiedosto**: `app/services/sentinel_learning_engine.py` (1012 riviä)

**Tarkoitus**: Käyttäjän oppimisen seuranta

**Ominaisuudet**:
- Käyttäytymismallien oppiminen
- Henkilökohtaiset suositukset
- Oppimisen seuranta
- AI-mallien päivitys
- Suorituskyvyn optimointi
- Oppimisdata analyysi

**API Endpointit**:
```python
POST /api/v1/learning/update
GET /api/v1/learning/progress
GET /api/v1/learning/insights
POST /api/v1/learning/feedback
GET /api/v1/learning/models
```

### 7.4 CareerIntelligence™
**Tiedosto**: `app/services/career_intelligence.py` (790 riviä)

**Tarkoitus**: Urakehityksen neuvonta

**Ominaisuudet**:
- CV analyysi
- Urakehityksen suunnittelu
- Tulojen optimointi
- Koulutuksen suositukset
- Markkinatieto
- Uraohjelmat

**API Endpointit**:
```python
POST /api/v1/career/analyze-cv
GET /api/v1/career/insights
POST /api/v1/career/plan
GET /api/v1/career/recommendations
POST /api/v1/career/goals
GET /api/v1/career/market-data
```

### 7.5 PredictiveBudget™
**Tiedosto**: `app/services/predictive_budget.py` (715 riviä)

**Tarkoitus**: Budjetin ennustaminen

**Ominaisuudet**:
- ARIMA-mallit
- 3 kuukauden ennusteet
- Kalenteriintegraatio
- Anomalian tunnistus
- Budjetin optimointi
- Trendianalyysi

**API Endpointit**:
```python
GET /api/v1/budget/predict
GET /api/v1/budget/forecast
POST /api/v1/budget/optimize
GET /api/v1/budget/trends
POST /api/v1/budget/plan
GET /api/v1/budget/accuracy
```

---

## 🔄 Automaatio

### 8.1 SchedulerService
**Tiedosto**: `app/services/scheduler_service.py` (935 riviä)

**Tarkoitus**: Taustaprosessien ajastus

**Ominaisuudet**:
- Cron-tyyliset ajastukset
- Taustaprosessien hallinta
- Virheenkäsittely
- Lokitus
- Suorituskyvyn seuranta
- Automaattinen uudelleenkäynnistys

**API Endpointit**:
```python
GET /api/v1/scheduler/status
POST /api/v1/scheduler/jobs
GET /api/v1/scheduler/jobs/{job_id}
DELETE /api/v1/scheduler/jobs/{job_id}
POST /api/v1/scheduler/trigger/{job_id}
GET /api/v1/scheduler/logs
```

### 8.2 EventBus
**Tiedosto**: `app/services/event_bus.py` (242 riviä)

**Tarkoitus**: Tapahtumien hallinta

**Ominaisuudet**:
- Tapahtumien julkaisu/tilaus
- Asynkroninen käsittely
- Virheenkäsittely
- Lokitus
- Suorituskyvyn optimointi
- Tapahtumien filtteröinti

**Käyttöesimerkki**:
```python
from app.services.event_bus import EventBus, EventType

# Palvelun alustus
event_bus = EventBus()

# Tapahtuman julkaisu
await event_bus.publish(
    event_type=EventType.TRANSACTION_CREATED,
    data={"user_id": 1, "amount": 45.67}
)

# Tapahtuman kuuntelu
@event_bus.subscribe(EventType.TRANSACTION_CREATED)
async def handle_transaction_created(data):
    # Käsittele tapahtuma
    await process_transaction(data)
```

---

## 🛡️ Turvallisuus

### 9.1 FinancialShield™
**Tiedosto**: `app/services/financial_shield.py` (597 riviä)

**Tarkoitus**: Taloudellinen suoja

**Ominaisuudet**:
- Petosten tunnistus
- Turvallisuusaudit
- Salasanan vahvuus
- Tietojen salaus
- Riskien arviointi
- Hälytysten hallinta

**API Endpointit**:
```python
POST /api/v1/shield/analyze
GET /api/v1/shield/risks
POST /api/v1/shield/audit
GET /api/v1/shield/alerts
POST /api/v1/shield/configure
GET /api/v1/shield/report
```

### 9.2 GuardianService
**Tiedosto**: `app/api/guardian.py` (366 riviä)

**Tarkoitus**: Järjestelmän valvonta

**Ominaisuudet**:
- Käyttäjien valvonta
- Rajoitusten hallinta
- Turvallisuusraportit
- Hälytysten hallinta
- Käyttäjien ryhmät
- Oikeuksien hallinta

**API Endpointit**:
```python
GET /api/v1/guardian/users
POST /api/v1/guardian/restrictions
GET /api/v1/guardian/reports
POST /api/v1/guardian/alerts
GET /api/v1/guardian/analytics
POST /api/v1/guardian/configure
```

---

## 📱 Käyttöliittymä

### Streamlit Frontend
**Tiedosto**: `personal_finance_agent/streamlit_app.py` (650+ riviä)

**Ominaisuudet**:
- Suomenkielinen käyttöliittymä
- Reaaliaikainen päivitys
- Interaktiiviset kaaviot
- Responsiivinen design
- Mobiiliystävällinen
- Pimeä/vaalea teema

**Sivut**:
- Dashboard (yleiskatsaus)
- Transaktiot (kulujen hallinta)
- Dokumentit (tiedostojen lataus)
- Analytiikka (tilastot)
- Tavoitteet (säästöjen seuranta)
- Asetukset (konfiguraatio)

**Käyttöesimerkki**:
```python
import streamlit as st
from app.services.api_client import APIClient

# API asiakas
api_client = APIClient("http://localhost:8000")

# Kirjautuminen
if st.button("Käytä demo-tiliä"):
    success, data = api_client.login("demo@example.com", "DemoPass123")
    if success:
        st.session_state.logged_in = True
        st.session_state.user = data["user"]

# Dashboard
if st.session_state.get("logged_in"):
    summary = api_client.get_dashboard_summary()
    st.metric("Säästöt", f"{summary['savings_to_date']:.2f}€")
```

---

## 🎯 Yhteenveto

Sentinel 100K sisältää 16 eri palvelua, jotka kattavat kaikki henkilökohtaisen rahoituksen tarpeet:

✅ **Autentikointi ja turvallisuus** (3 palvelua)
✅ **Datan käsittely** (3 palvelua)  
✅ **AI ja koneoppiminen** (5 palvelua)
✅ **Automaatio ja seuranta** (3 palvelua)
✅ **Käyttäjien hallinta** (2 palvelua)

**Kokonaismäärä**: 6,000+ riviä tuotantokoodia
**API endpointit**: 50+ endpointia
**Tietokantamallit**: 10+ taulua
**AI-mallit**: 5+ eri mallia

Kaikki palvelut ovat modulaarisia ja voidaan käyttää itsenäisesti tai yhdessä muiden palveluiden kanssa. Järjestelmä on suunniteltu skaalautuvaksi ja ylläpidettäväksi.

---

**Luotu**: Sentinel 100K Development Team  
**Versio**: 1.0.0  
**Päivitetty**: 2024-01-15  
**Status**: Production Ready ✅ 