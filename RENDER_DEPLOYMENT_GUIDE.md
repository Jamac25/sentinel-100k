# 🚀 Sentinel 100K - Render Käyttöönotto-ohje

## 📋 Sisällysluettelo

- [Yleiskatsaus](#yleiskatsaus)
- [Render-tili](#render-tili)
- [GitHub Repository](#github-repository)
- [Käyttöönotto](#käyttöönotto)
- [Ympäristömuuttujat](#ympäristömuuttujat)
- [Tietokanta](#tietokanta)
- [AI-palvelut](#ai-palvelut)
- [Testaus](#testaus)
- [Seuranta](#seuranta)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Yleiskatsaus

Tämä ohje kattaa Sentinel 100K -järjestelmän käyttöönoton Render-palveluun. Render on moderni cloud-platform, joka tukee Python-sovelluksia, tietokantoja ja Redis-cachea.

### 🏗️ Järjestelmän komponentit Renderissä
- **Backend API**: FastAPI-pohjainen REST API
- **Frontend**: Streamlit-pohjainen käyttöliittymä
- **Worker**: Taustaprosessit ja ajastukset
- **PostgreSQL**: Tietokanta
- **Redis**: Cache ja session storage

---

## 📝 Render-tili

### 1. Tilin luominen

1. Mene [render.com](https://render.com)
2. Klikkaa "Get Started"
3. Rekisteröidy GitHub-tilillä
4. Valitse "Free" tai "Paid" suunnitelma

### 2. Suunnitelmat

**Free Tier (Kokeilu):**
- 750 tuntia/kuukausi
- 512 MB RAM per palvelu
- Shared CPU
- PostgreSQL 1 GB
- Redis 25 MB

**Paid Tier (Tuotanto):**
- $7/kuukausi per palvelu
- 1 GB RAM per palvelu
- Dedicated CPU
- PostgreSQL 1 GB
- Redis 100 MB

---

## 🔗 GitHub Repository

### 1. Repositoryn valmistelu

```bash
# Varmista että kaikki tiedostot on commitattu
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Tärkeät tiedostot

Varmista että seuraavat tiedostot ovat repositoryssa:

```
sentinel-100k/
├── render.yaml              # Render konfiguraatio
├── requirements.txt          # Python riippuvuudet
├── app/                      # Sovelluskoodi
├── streamlit_app.py         # Frontend
├── docs/                     # Dokumentaatio
└── README.md                # Päädokumentaatio
```

---

## 🚀 Käyttöönotto

### 1. Blueprint käyttöönotto

1. **Mene Render Dashboard**
   - Kirjaudu [dashboard.render.com](https://dashboard.render.com)

2. **Luo Blueprint**
   - Klikkaa "New +"
   - Valitse "Blueprint"
   - Klikkaa "Connect" GitHub-tilillesi

3. **Valitse Repository**
   - Etsi `sentinel-100k` repository
   - Klikkaa "Connect"

4. **Konfiguroi Blueprint**
   - Nimi: `sentinel-100k`
   - Branch: `main`
   - Klikkaa "Apply"

### 2. Palveluiden luominen

Render luo automaattisesti seuraavat palvelut:

- **sentinel-100k-api** (Web Service)
- **sentinel-100k-frontend** (Web Service)
- **sentinel-100k-worker** (Worker Service)
- **sentinel-db** (PostgreSQL Database)
- **sentinel-redis** (Redis Cache)

### 3. Käyttöönoton seuranta

```bash
# Tarkista deploy-tila
# Mene Render Dashboard -> sentinel-100k-api -> Logs
```

---

## ⚙️ Ympäristömuuttujat

### 1. API Service (sentinel-100k-api)

Mene **sentinel-100k-api** -> **Environment** ja lisää:

```env
# Perusasetukset
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Tietokanta (Render luo automaattisesti)
DATABASE_URL=postgresql://sentinel_user:password@host:port/sentinel_db

# Redis (Render luo automaattisesti)
REDIS_URL=redis://host:port

# Tietoturva (Render generoi automaattisesti)
SECRET_KEY=render-generated-secret
JWT_SECRET_KEY=render-generated-jwt-secret

# AI-palvelut (lisää manuaalisesti)
OPENAI_API_KEY=sk-your-openai-api-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# OCR-palvelut
TESSERACT_PATH=/usr/bin/tesseract
OCR_LANGUAGE=fin+eng

# Tiedostojen käsittely
UPLOAD_DIR=/opt/render/project/src/uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# Sähköposti
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Frontend Service (sentinel-100k-frontend)

```env
PYTHON_VERSION=3.11.0
API_BASE_URL=https://sentinel-100k-api.onrender.com
ENVIRONMENT=production
```

### 3. Worker Service (sentinel-100k-worker)

```env
PYTHON_VERSION=3.11.0
ENVIRONMENT=production
DATABASE_URL=postgresql://sentinel_user:password@host:port/sentinel_db
REDIS_URL=redis://host:port
SECRET_KEY=render-generated-secret
OPENAI_API_KEY=sk-your-openai-api-key
LOG_LEVEL=INFO
```

---

## 🗄️ Tietokanta

### 1. PostgreSQL konfiguraatio

Render luo automaattisesti PostgreSQL-tietokannan:

- **Nimi**: sentinel-db
- **Käyttäjä**: sentinel_user
- **Salasana**: Render generoi automaattisesti
- **Koko**: 1 GB (Free tier)

### 2. Tietokannan alustus

```bash
# Tietokannan alustus tapahtuu automaattisesti
# kun API-palvelu käynnistyy ensimmäisen kerran
```

### 3. Tietokannan hallinta

```bash
# Mene Render Dashboard -> sentinel-db
# Klikkaa "Connect" nähdäksesi yhteystiedot

# Tietokannan yhteystiedot:
Host: host.render.com
Port: 5432
Database: sentinel_db
Username: sentinel_user
Password: render-generated-password
```

---

## 🤖 AI-palvelut

### 1. OpenAI API

1. **Hanki API-avain**
   - Mene [platform.openai.com](https://platform.openai.com)
   - Luo uusi API-avain

2. **Lisää Renderiin**
   - Mene sentinel-100k-api -> Environment
   - Lisää: `OPENAI_API_KEY=sk-your-key`

### 2. Google Vision API

1. **Luo Google Cloud Project**
   - Mene [console.cloud.google.com](https://console.cloud.google.com)
   - Ota Google Vision API käyttöön

2. **Luo Service Account**
   - IAM & Admin -> Service Accounts
   - Luo uusi service account
   - Lataa JSON credentials

3. **Lisää Renderiin**
   - Lisää credentials.json repositoryyn
   - Lisää ympäristömuuttuja: `GOOGLE_APPLICATION_CREDENTIALS=/opt/render/project/src/credentials.json`

### 3. Paikalliset ML-mallit

```bash
# ML-mallit koulutetaan automaattisesti
# kun worker-palvelu käynnistyy ensimmäisen kerran
```

---

## 🧪 Testaus

### 1. API testaus

```bash
# Testaa API endpointit
curl https://sentinel-100k-api.onrender.com/api/v1/health

# Testaa autentikointi
curl -X POST https://sentinel-100k-api.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"DemoPass123"}'
```

### 2. Frontend testaus

```bash
# Avaa selain
https://sentinel-100k-frontend.onrender.com

# Testaa demo-tili
Email: demo@example.com
Password: DemoPass123
```

### 3. Tietokanta testaus

```bash
# Tarkista tietokantayhteys
# Mene sentinel-db -> Connect -> External Database URL
psql "postgresql://sentinel_user:password@host:port/sentinel_db"

# Testaa taulut
\dt
SELECT COUNT(*) FROM users;
```

---

## 📊 Seuranta

### 1. Logien seuranta

```bash
# API logit
# Mene sentinel-100k-api -> Logs

# Frontend logit
# Mene sentinel-100k-frontend -> Logs

# Worker logit
# Mene sentinel-100k-worker -> Logs
```

### 2. Suorituskyvyn seuranta

```bash
# Mene palvelu -> Metrics
# Tarkista:
# - CPU käyttö
# - Muistin käyttö
# - Verkkoliikenne
# - Response times
```

### 3. Virheiden seuranta

```bash
# Mene palvelu -> Logs
# Etsi ERROR-tason viestejä
# Tarkista failed deployments
```

---

## 🔧 Troubleshooting

### 1. Yleisimmät ongelmat

#### Build epäonnistuu
```bash
# Tarkista requirements.txt
# Varmista että kaikki riippuvuudet on listattu
# Tarkista Python version (3.11.0)

# Tarkista build logit
# Mene palvelu -> Logs -> Build Logs
```

#### Sovellus ei käynnisty
```bash
# Tarkista startCommand
# Varmista että portti on $PORT
# Tarkista ympäristömuuttujat

# Tarkista runtime logit
# Mene palvelu -> Logs -> Runtime Logs
```

#### Tietokantayhteys ei toimi
```bash
# Tarkista DATABASE_URL
# Varmista että tietokanta on luotu
# Tarkista credentials

# Testaa yhteys
# Mene sentinel-db -> Connect
```

#### AI-palvelut eivät toimi
```bash
# Tarkista API-avaimet
# Varmista että avaimet on lisätty ympäristömuuttujiin
# Tarkista API-kutsujen logit
```

### 2. Debug-tila

```bash
# Ota debug-tila käyttöön
# Lisää ympäristömuuttuja: DEBUG=true

# Tarkista yksityiskohtaiset logit
# Mene palvelu -> Logs
```

### 3. Palvelun uudelleenkäynnistys

```bash
# Mene palvelu -> Manual Deploy
# Klikkaa "Deploy latest commit"

# Tai käynnistä uudelleen
# Mene palvelu -> Settings -> Restart Service
```

---

## 📈 Skalaus

### 1. Automaattinen skaalaus

```bash
# Mene palvelu -> Settings -> Auto-Deploy
# Ota automaattinen skaalaus käyttöön

# Aseta skaalausrajoitukset
# Min instances: 1
# Max instances: 10
```

### 2. Manuaalinen skaalaus

```bash
# Mene palvelu -> Settings -> Instance Type
# Valitse suurempi instanssi:
# - Starter: 512 MB RAM
# - Standard: 1 GB RAM
# - Pro: 2 GB RAM
```

### 3. Tietokannan skaalaus

```bash
# Mene sentinel-db -> Settings
# Valitse suurempi suunnitelma:
# - Starter: 1 GB
# - Standard: 10 GB
# - Pro: 100 GB
```

---

## 💰 Kustannukset

### Free Tier (Kokeilu)
- **API Service**: 750h/kk
- **Frontend Service**: 750h/kk
- **Worker Service**: 750h/kk
- **PostgreSQL**: 1 GB
- **Redis**: 25 MB
- **Kokonaiskustannus**: $0/kk

### Paid Tier (Tuotanto)
- **API Service**: $7/kk
- **Frontend Service**: $7/kk
- **Worker Service**: $7/kk
- **PostgreSQL**: $7/kk
- **Redis**: $7/kk
- **Kokonaiskustannus**: $35/kk

---

## 📞 Tuki

### Render Support
- **Dokumentaatio**: [docs.render.com](https://docs.render.com)
- **Discord**: [discord.gg/render](https://discord.gg/render)
- **Email**: support@render.com

### Sentinel 100K Support
- **Dokumentaatio**: [docs.sentinel-100k.com](https://docs.sentinel-100k.com)
- **GitHub Issues**: [github.com/your-org/sentinel-100k/issues](https://github.com/your-org/sentinel-100k/issues)
- **Email**: support@sentinel-100k.com

---

## ✅ Käyttöönotto valmis!

Kun olet seurannut tätä ohjetta, sinulla on:

✅ **Täysin toimiva Sentinel 100K -järjestelmä**  
✅ **Automaattinen skaalaus**  
✅ **Tuotantovalmiit palvelut**  
✅ **Tietokanta ja cache**  
✅ **AI-palvelut integroituna**  
✅ **Seuranta ja lokitus**  

**URL:t:**
- **API**: https://sentinel-100k-api.onrender.com
- **Frontend**: https://sentinel-100k-frontend.onrender.com
- **Dokumentaatio**: https://docs.sentinel-100k.com

---

**Luotu**: Sentinel 100K Development Team  
**Versio**: 1.0.0  
**Päivitetty**: 2024-01-15  
**Status**: Render Ready ✅ 