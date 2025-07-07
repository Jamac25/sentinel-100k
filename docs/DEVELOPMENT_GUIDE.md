# 👨‍💻 Sentinel 100K - Kehitysohje

## 📋 Sisällysluettelo

- [Yleiskatsaus](#yleiskatsaus)
- [Kehitysympäristön asennus](#kehitysympäristön-asennus)
- [Projektin rakenne](#projektin-rakenne)
- [Koodaustyylit](#koodaustyylit)
- [Testaus](#testaus)
- [Dokumentaatio](#dokumentaatio)
- [Git workflow](#git-workflow)
- [Debugging](#debugging)
- [Suorituskyvyn optimointi](#suorituskyvyn-optimointi)
- [Turvallisuus](#turvallisuus)

---

## 🎯 Yleiskatsaus

Tämä ohje on tarkoitettu Sentinel 100K -järjestelmän kehittäjille ja kontribuuttoreille. Se kattaa kaikki kehitystyön kannalta tärkeät asiat, koodaustyylit ja best practices.

### 🛠️ Kehitystyökalut
- **IDE**: VS Code, PyCharm tai Vim
- **Python**: 3.11+
- **Tietokanta**: SQLite (kehitys), PostgreSQL (tuotanto)
- **Testaus**: pytest, coverage
- **Linting**: flake8, black, isort
- **Type checking**: mypy
- **Dokumentaatio**: Sphinx, MkDocs

---

## 💻 Kehitysympäristön asennus

### 1. Perusasetukset

```bash
# Kloonaa repository
git clone https://github.com/your-org/sentinel-100k.git
cd sentinel-100k

# Luo virtuaaliympäristö
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Asenna riippuvuudet
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Pre-commit hooks

```bash
# Asenna pre-commit
pip install pre-commit

# Asenna git hooks
pre-commit install

# Testaa hooks
pre-commit run --all-files
```

### 3. Ympäristömuuttujat (kehitys)

```bash
# Luo .env.development tiedosto
cp .env.example .env.development

# Muokkaa kehitysasetukset
nano .env.development
```

```env
# Kehitysasetukset
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Tietokanta (SQLite kehityksessä)
DATABASE_URL=sqlite:///./sentinel_dev.db

# AI-palvelut (mock kehityksessä)
OPENAI_API_KEY=mock-key-for-development
USE_MOCK_AI=true

# OCR (paikallinen kehityksessä)
TESSERACT_PATH=/usr/bin/tesseract
USE_LOCAL_OCR=true

# Lokitus
LOG_FILE=./logs/app.log
ERROR_LOG_FILE=./logs/errors.log
```

### 4. Tietokannan alustus

```bash
# Luo kehitystietokanta
python -m app.db.init_db --env development

# Lisää testidataa
python scripts/seed_test_data.py
```

---

## 📁 Projektin rakenne

```
sentinel-100k/
├── app/                          # Pääsovellus
│   ├── api/                      # API endpointit
│   │   ├── auth.py              # Autentikointi
│   │   ├── transactions.py      # Transaktiot
│   │   ├── dashboard.py         # Dashboard
│   │   └── guardian.py          # Järjestelmän valvonta
│   ├── core/                     # Ydinasetukset
│   │   ├── config.py            # Konfiguraatio
│   │   └── security.py          # Turvallisuus
│   ├── db/                       # Tietokanta
│   │   ├── base.py              # Tietokannan perusta
│   │   └── init_db.py           # Alustus
│   ├── models/                   # Tietokantamallit
│   │   ├── user.py              # Käyttäjämalli
│   │   ├── transaction.py       # Transaktiomalli
│   │   └── document.py          # Dokumenttimalli
│   ├── schemas/                  # Pydantic skeemat
│   │   ├── auth.py              # Autentikaatioskeemat
│   │   ├── transaction.py       # Transaktioskeemat
│   │   └── user.py              # Käyttäjäskeemat
│   ├── services/                 # Bisneslogiikka
│   │   ├── auth_service.py      # Autentikaatiopalvelu
│   │   ├── transaction_service.py # Transaktiopalvelu
│   │   └── ai_services/         # AI-palvelut
│   └── main.py                   # Sovelluksen pääohjelma
├── tests/                        # Testit
│   ├── conftest.py              # pytest konfiguraatio
│   ├── test_api/                # API testit
│   ├── test_services/           # Palvelutestit
│   └── test_models/             # Mallitestit
├── docs/                         # Dokumentaatio
├── scripts/                      # Skriptit
├── requirements.txt              # Riippuvuudet
├── requirements-dev.txt          # Kehitysriippuvuudet
└── README.md                     # Päädokumentaatio
```

---

## 📝 Koodaustyylit

### 1. Python koodaustyylit

```python
# ✅ Hyvä esimerkki
from typing import Optional, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TransactionService:
    """Transaktioiden käsittelypalvelu."""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def create_transaction(
        self, 
        user_id: int, 
        amount: float, 
        description: str,
        category: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Luo uusi transaktio.
        
        Args:
            user_id: Käyttäjän ID
            amount: Summa
            description: Kuvaus
            category: Kategoria (valinnainen)
            
        Returns:
            Luodun transaktion tiedot
            
        Raises:
            ValueError: Jos summa on negatiivinen
        """
        if amount < 0:
            raise ValueError("Summa ei voi olla negatiivinen")
        
        try:
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                description=description,
                category=category,
                created_at=datetime.utcnow()
            )
            
            self.db_session.add(transaction)
            await self.db_session.commit()
            
            logger.info(f"Luotu transaktio {transaction.id} käyttäjälle {user_id}")
            
            return {
                "id": transaction.id,
                "amount": transaction.amount,
                "description": transaction.description,
                "category": transaction.category,
                "created_at": transaction.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Virhe transaktion luomisessa: {e}")
            await self.db_session.rollback()
            raise
```

### 2. API endpointit

```python
# ✅ Hyvä API endpoint
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService
from app.core.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user = Depends(get_current_user),
    transaction_service: TransactionService = Depends()
):
    """
    Luo uusi transaktio.
    
    - **amount**: Transaktion summa
    - **description**: Transaktion kuvaus
    - **category**: Kategoria (valinnainen)
    """
    try:
        transaction = await transaction_service.create_transaction(
            user_id=current_user.id,
            amount=transaction_data.amount,
            description=transaction_data.description,
            category=transaction_data.category
        )
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Virhe transaktion luomisessa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sisäinen palvelinvirhe"
        )


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    transaction_service: TransactionService = Depends()
):
    """
    Hae käyttäjän transaktiot.
    
    - **skip**: Montako transaktiota ohitetaan
    - **limit**: Maksimimäärä transaktioita
    """
    transactions = await transaction_service.get_user_transactions(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return transactions
```

### 3. Tietokantamallit

```python
# ✅ Hyvä tietokantamalli
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Transaction(Base):
    """Transaktioiden tietokantamalli."""
    
    __tablename__ = "transactions"
    
    # Perustiedot
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    
    # Aikaleimat
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Suhteet
    user = relationship("User", back_populates="transactions")
    
    # Indeksit suorituskyvyn parantamiseen
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'created_at'),
        Index('idx_category_amount', 'category', 'amount'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description='{self.description}')>"
```

---

## 🧪 Testaus

### 1. Testien rakenne

```python
# tests/test_services/test_transaction_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.transaction_service import TransactionService
from app.models.transaction import Transaction


class TestTransactionService:
    """TransactionService testit."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock tietokantasesio."""
        session = Mock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def transaction_service(self, mock_db_session):
        """TransactionService instanssi."""
        return TransactionService(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_create_transaction_success(self, transaction_service, mock_db_session):
        """Testaa onnistuneen transaktion luomisen."""
        # Arrange
        user_id = 1
        amount = 100.0
        description = "Test transaction"
        category = "test"
        
        # Act
        result = await transaction_service.create_transaction(
            user_id=user_id,
            amount=amount,
            description=description,
            category=category
        )
        
        # Assert
        assert result["amount"] == amount
        assert result["description"] == description
        assert result["category"] == category
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_transaction_negative_amount(self, transaction_service):
        """Testaa negatiivisen summan käsittelyn."""
        # Arrange
        user_id = 1
        amount = -100.0
        description = "Test transaction"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Summa ei voi olla negatiivinen"):
            await transaction_service.create_transaction(
                user_id=user_id,
                amount=amount,
                description=description
            )
    
    @pytest.mark.asyncio
    async def test_create_transaction_database_error(self, transaction_service, mock_db_session):
        """Testaa tietokantavirheen käsittelyn."""
        # Arrange
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            await transaction_service.create_transaction(
                user_id=1,
                amount=100.0,
                description="Test"
            )
        
        mock_db_session.rollback.assert_called_once()
```

### 2. API testit

```python
# tests/test_api/test_transactions.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestTransactionAPI:
    """Transaktioiden API testit."""
    
    @pytest.fixture
    def auth_headers(self):
        """Autentikaatio headers."""
        # Tässä käytetään test-tokenia
        return {"Authorization": "Bearer test-token"}
    
    def test_create_transaction_success(self, auth_headers):
        """Testaa onnistuneen transaktion luomisen."""
        # Arrange
        transaction_data = {
            "amount": 100.0,
            "description": "Test transaction",
            "category": "test"
        }
        
        # Act
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 100.0
        assert data["description"] == "Test transaction"
        assert data["category"] == "test"
    
    def test_create_transaction_unauthorized(self):
        """Testaa kirjautumattoman käyttäjän käsittelyn."""
        # Arrange
        transaction_data = {
            "amount": 100.0,
            "description": "Test transaction"
        }
        
        # Act
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_create_transaction_invalid_data(self, auth_headers):
        """Testaa virheellisen datan käsittelyn."""
        # Arrange
        transaction_data = {
            "amount": -100.0,  # Negatiivinen summa
            "description": "Test transaction"
        }
        
        # Act
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        assert "negatiivinen" in response.json()["detail"].lower()
```

### 3. Testien ajo

```bash
# Kaikki testit
pytest

# Tietty testitiedosto
pytest tests/test_services/test_transaction_service.py

# Tietty testi
pytest tests/test_services/test_transaction_service.py::TestTransactionService::test_create_transaction_success

# Coverage raportti
pytest --cov=app --cov-report=html

# Nopeat testit (ilman integraatiotestejä)
pytest -m "not integration"

# Integraatiotestit
pytest -m integration
```

---

## 📚 Dokumentaatio

### 1. Docstring-tyylit

```python
def calculate_monthly_budget(
    income: float,
    fixed_expenses: List[float],
    savings_goal: float
) -> Dict[str, float]:
    """
    Laske kuukausibudjetti annettujen parametrien perusteella.
    
    Args:
        income: Kuukausitulot euroissa
        fixed_expenses: Lista kiinteistä kuluista euroissa
        savings_goal: Säästötavoite euroissa
        
    Returns:
        Sanakirja budjetin tiedoilla:
        - 'disposable_income': Käytettävissä oleva tulo
        - 'total_expenses': Kokonaiskulut
        - 'savings_rate': Säästöaste prosentteina
        
    Raises:
        ValueError: Jos tulot ovat negatiiviset
        ValueError: Jos säästötavoite on suurempi kuin tulot
        
    Example:
        >>> budget = calculate_monthly_budget(3000, [800, 200, 150], 500)
        >>> print(budget['disposable_income'])
        1350.0
    """
    if income < 0:
        raise ValueError("Tulot eivät voi olla negatiiviset")
    
    total_expenses = sum(fixed_expenses)
    disposable_income = income - total_expenses
    
    if savings_goal > disposable_income:
        raise ValueError("Säästötavoite on liian suuri")
    
    savings_rate = (savings_goal / income) * 100
    
    return {
        'disposable_income': disposable_income,
        'total_expenses': total_expenses,
        'savings_rate': savings_rate
    }
```

### 2. API dokumentaatio

```python
@router.post("/budget/calculate", response_model=BudgetResponse)
async def calculate_budget(
    request: BudgetRequest,
    current_user = Depends(get_current_user)
):
    """
    Laske henkilökohtainen budjetti.
    
    Tämä endpoint laskee käyttäjän kuukausibudjetin annettujen 
    parametrien perusteella ja palauttaa yksityiskohtaisen 
    budjettisuunnitelman.
    
    ## Parametrit
    
    - **income**: Kuukausitulot euroissa (min. 0)
    - **fixed_expenses**: Lista kiinteistä kuluista
    - **savings_goal**: Kuukausittainen säästötavoite
    
    ## Vastaus
    
    Palauttaa JSON-objektin, joka sisältää:
    - **disposable_income**: Käytettävissä oleva tulo
    - **total_expenses**: Kokonaiskulut
    - **savings_rate**: Säästöaste prosentteina
    - **recommendations**: Budjettisuositukset
    
    ## Virhekoodit
    
    - **400**: Virheelliset parametrit
    - **401**: Ei autentikaatiota
    - **500**: Sisäinen palvelinvirhe
    
    ## Esimerkki
    
    ```json
    {
        "income": 3000,
        "fixed_expenses": [800, 200, 150],
        "savings_goal": 500
    }
    ```
    """
    # Toteutus...
```

---

## 🔄 Git Workflow

### 1. Branch-strategia

```bash
# Päähaarat
main          # Tuotantoversio
develop       # Kehitysversio
feature/*     # Uudet ominaisuudet
bugfix/*      # Virheiden korjaukset
hotfix/*      # Kriittiset korjaukset

# Esimerkki workflow
git checkout develop
git pull origin develop
git checkout -b feature/new-transaction-service
# Tee muutokset
git add .
git commit -m "feat: Add new transaction service with AI categorization"
git push origin feature/new-transaction-service
# Luo pull request
```

### 2. Commit-viestit

```bash
# Hyvä commit-viesti
feat: Add AI-powered transaction categorization

- Implement machine learning model for automatic categorization
- Add support for 15 different expense categories
- Include confidence scoring for predictions
- Add user feedback mechanism for model improvement

Closes #123

# Commit-tyypit
feat:     Uusi ominaisuus
fix:      Virheiden korjaus
docs:     Dokumentaation päivitys
style:    Koodaustyylin muutokset
refactor: Koodin refaktorointi
test:     Testien lisäys tai muutos
chore:    Muut muutokset
```

### 3. Pull Request template

```markdown
## 📝 Kuvaus
Lyhyt kuvaus muutoksista.

## 🎯 Tyyppi
- [ ] Uusi ominaisuus
- [ ] Virheiden korjaus
- [ ] Dokumentaation päivitys
- [ ] Koodaustyylin muutos
- [ ] Refaktorointi

## 🧪 Testit
- [ ] Yksikkötestit lisätty/päivitetty
- [ ] Integraatiotestit lisätty/päivitetty
- [ ] Kaikki testit menevät läpi

## 📚 Dokumentaatio
- [ ] API dokumentaatio päivitetty
- [ ] README päivitetty
- [ ] Kommentit lisätty koodiin

## 🔍 Tarkistuslista
- [ ] Koodi noudattaa koodaustyylejä
- [ ] Ei console.log tai print-lauseita
- [ ] Virheenkäsittely on kunnossa
- [ ] Suorituskyky on testattu

## 📸 Screenshotit (jos soveltuu)
Lisää screenshotit UI-muutoksista.

## 🔗 Liittyy
Closes #123
```

---

## 🐛 Debugging

### 1. Logging

```python
import logging
from app.core.config import settings

# Loggerin konfiguraatio
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

# Eri logitasot
logger.debug("Debug-viesti")
logger.info("Info-viesti")
logger.warning("Varoitus")
logger.error("Virhe")
logger.critical("Kriittinen virhe")

# Strukturoitu logging
logger.info("Transaktio luotu", extra={
    "user_id": user_id,
    "amount": amount,
    "transaction_id": transaction.id
})
```

### 2. Debug-tila

```python
# app/core/config.py
class Settings:
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    @property
    def log_level(self) -> str:
        return "DEBUG" if self.DEBUG else "INFO"

# Käyttö
if settings.DEBUG:
    logger.debug(f"Request data: {request_data}")
    logger.debug(f"Database query: {query}")
```

### 3. Pytest debugging

```python
# Testien debug-tila
pytest --pdb  # Pysäytä virheeseen
pytest --pdbcls=IPython.terminal.debugger:Pdb  # IPython debugger

# Tietty testi debug-tilassa
pytest tests/test_services/test_transaction_service.py::test_create_transaction_success --pdb
```

---

## ⚡ Suorituskyvyn optimointi

### 1. Tietokanta optimointi

```python
# Indeksien lisäys
class Transaction(Base):
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'created_at'),
        Index('idx_category_amount', 'category', 'amount'),
        Index('idx_user_category', 'user_id', 'category'),
    )

# Query optimointi
async def get_user_transactions_optimized(self, user_id: int, limit: int = 100):
    """Optimoidut transaktioiden haut."""
    query = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .options(selectinload(Transaction.user))  # Eager loading
    )
    
    result = await self.db_session.execute(query)
    return result.scalars().all()

# Bulk operaatiot
async def create_transactions_bulk(self, transactions: List[Dict]):
    """Useita transaktioita kerralla."""
    transaction_objects = [
        Transaction(**transaction_data)
        for transaction_data in transactions
    ]
    
    self.db_session.add_all(transaction_objects)
    await self.db_session.commit()
```

### 2. Caching

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time: int = 3600):
    """Cache-dekoratiivi."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Luo cache-avain
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Tarkista cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Suorita funktio
            result = await func(*args, **kwargs)
            
            # Tallenna cacheen
            redis_client.setex(
                cache_key,
                expire_time,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# Käyttö
@cache_result(expire_time=1800)  # 30 minuuttia
async def get_dashboard_summary(self, user_id: int):
    """Dashboard yhteenveto cacheen tallennettuna."""
    # Kalliit laskelmat...
    return summary_data
```

### 3. Asynkroninen käsittely

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class TransactionService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_transactions_async(self, transactions: List[Dict]):
        """Käsittele transaktiot asynkronisesti."""
        tasks = []
        
        for transaction in transactions:
            task = asyncio.create_task(
                self.process_single_transaction(transaction)
            )
            tasks.append(task)
        
        # Suorita kaikki samanaikaisesti
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Käsittele tulokset
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        return {
            "successful": len(successful),
            "failed": len(failed),
            "errors": failed
        }
    
    async def process_single_transaction(self, transaction: Dict):
        """Käsittele yksi transaktio."""
        # CPU-intensiivinen käsittely thread poolissa
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._process_transaction_cpu_intensive,
            transaction
        )
        return result
```

---

## 🔒 Turvallisuus

### 1. Input validointi

```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, le=1000000)  # 0 < amount <= 1M
    description: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    
    @validator('description')
    def validate_description(cls, v):
        """Validoi kuvauksen sisältö."""
        # Estä SQL injection -yritykset
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            if char in v.lower():
                raise ValueError(f"Kuvaus sisältää kiellettyjä merkkejä: {char}")
        return v
    
    @validator('category')
    def validate_category(cls, v):
        """Validoi kategorian."""
        if v:
            allowed_categories = [
                'ruoka', 'kuljetus', 'viihde', 'terveys',
                'asuminen', 'vaatteet', 'koulutus', 'muu'
            ]
            if v.lower() not in allowed_categories:
                raise ValueError(f"Virheellinen kategoria: {v}")
        return v.lower() if v else v
```

### 2. SQL injection suojaus

```python
# ✅ Turvallinen
async def get_user_transactions_safe(self, user_id: int):
    """Turvallinen transaktioiden haku."""
    query = select(Transaction).where(Transaction.user_id == user_id)
    result = await self.db_session.execute(query)
    return result.scalars().all()

# ❌ Vaarallinen
async def get_user_transactions_unsafe(self, user_id: str):
    """Vaarallinen transaktioiden haku."""
    query = f"SELECT * FROM transactions WHERE user_id = {user_id}"
    # Tämä on haavoittuva SQL injection -hyökkäyksille
```

### 3. Rate limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@router.post("/transactions/")
@limiter.limit("10/minute")  # 10 kutsua minuutissa
async def create_transaction(
    request: Request,
    transaction_data: TransactionCreate,
    current_user = Depends(get_current_user)
):
    """Luo transaktio rate limiting -suojauksella."""
    # Toteutus...
```

---

## 📞 Tuki ja resursseja

### Hyödyllisiä linkkejä

- **FastAPI dokumentaatio**: https://fastapi.tiangolo.com/
- **SQLAlchemy dokumentaatio**: https://docs.sqlalchemy.org/
- **Pytest dokumentaatio**: https://docs.pytest.org/
- **Python type hints**: https://docs.python.org/3/library/typing.html

### Kehitystiimi

- **Tech Lead**: tech-lead@sentinel-100k.com
- **Senior Developer**: senior-dev@sentinel-100k.com
- **QA Engineer**: qa@sentinel-100k.com

### Code Review

- Kaikki pull requestit vaativat vähintään yhden hyväksynnän
- Kriittiset muutokset vaativat tech leadin hyväksynnän
- Testien coverage pitää olla vähintään 80%

---

**Luotu**: Sentinel 100K Development Team  
**Versio**: 1.0.0  
**Päivitetty**: 2024-01-15  
**Status**: Development Ready ✅ 