# Personal Finance Agent API - Käynnistysohje

## Pika-aloitus

### 1. Asenna riippuvuudet
```bash
cd personal_finance_agent
pip install -r requirements.txt
```

### 2. Luo ympäristömuuttujat
```bash
cp .env.example .env
# Muokkaa .env-tiedostoa tarpeen mukaan
```

### 3. Käynnistä API
```bash
python run_api.py
```

API käynnistyy osoitteeseen: `http://localhost:8000`

## API-dokumentaatio

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Käytettävissä olevat päätepisteet

### Autentikointi (`/api/v1/auth`)
- `POST /auth/register` - Rekisteröidy
- `POST /auth/login` - Kirjaudu sisään
- `GET /auth/me` - Omat tiedot

### Dokumentit (`/api/v1/documents`)
- `POST /documents/upload` - Lataa dokumentti
- `GET /documents/` - Listaa dokumentit
- `GET /documents/{id}` - Hae dokumentti

### Transaktiot (`/api/v1/transactions`)
- `POST /transactions/` - Luo transaktio
- `GET /transactions/` - Listaa transaktiot
- `PUT /transactions/{id}` - Päivitä transaktio

### Kategoriat (`/api/v1/categories`)
- `GET /categories/` - Listaa kategoriat
- `GET /categories/stats/usage` - Käyttötilastot

### Dashboard (`/api/v1/dashboard`)
- `GET /dashboard/summary` - Finanssiyhteenveto
- `GET /dashboard/insights/smart` - Älykkäät oivallukset

## Esimerkki käyttö

### 1. Rekisteröidy
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "SecurePass123"
  }'
```

### 2. Kirjaudu sisään
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

### 3. Käytä API:a tokenilla
```bash
# Tallenna token muuttujaan
TOKEN="your-jwt-token-here"

# Hae dashboard-yhteenveto
curl -X GET "http://localhost:8000/api/v1/dashboard/summary" \
  -H "Authorization: Bearer $TOKEN"
```

## Terveydentarkistus

```bash
curl http://localhost:8000/health
```

## Kehittäjätila

```bash
# Käynnistä debug-tilassa automaattisella uudelleenlatautumisella
export DEBUG=true
python run_api.py
```

## Docker (tuleva)

```bash
# Rakenna Docker-image
docker build -t personal-finance-agent .

# Käynnistä kontainer
docker run -p 8000:8000 personal-finance-agent
```

## Huomioita

- API käyttää SQLite-tietokantaa oletuksena
- Tiedostot tallennetaan `data/documents/` hakemistoon
- Logit kirjoitetaan `logs/` hakemistoon
- OCR-palvelu vaatii Tesseract-asennuksen

## Tuki

- API-dokumentaatio: `/docs`
- Logi-tiedostot: `logs/app.log`
- Konfiguraatio: `app/core/config.py` 