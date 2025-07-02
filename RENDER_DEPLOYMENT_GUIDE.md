# 🎯 SENTINEL 100K - RENDER.COM DEPLOYMENT GUIDE

## 🚀 Täydellinen opas Render.com-siirtoon

### 🎯 VAIHE 1: Render-tilin luominen

1. **Mene osoitteeseen**: https://render.com
2. **Rekisteröidy** GitHub-tilillä (suositeltava)
3. **Vahvista sähköposti**

### 📂 VAIHE 2: GitHub-repositoryn valmistelu

1. **Luo uusi repository GitHubissa** nimellä `sentinel-100k`
2. **Lataa kaikki tiedostot** repositoryyn:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Sentinel 100K complete"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/sentinel-100k.git
   git push -u origin main
   ```

### 🗄️ VAIHE 3: Tietokannan luominen

1. **Render Dashboardissa** → "New" → "PostgreSQL"
2. **Asetukset**:
   - Name: `sentinel-db`
   - Database: `sentinel_100k`
   - User: `sentinel_user`
   - Plan: **Free** (512MB)
3. **Luo tietokanta** → Odota 2-3 minuuttia

### 🌐 VAIHE 4: Web Service -luominen

1. **Render Dashboardissa** → "New" → "Web Service"
2. **Yhdistä GitHub repository** `sentinel-100k`
3. **Asetukset**:
   
   **Basic Settings:**
   - Name: `sentinel-100k`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn sentinel_render_ready:app --host 0.0.0.0 --port $PORT`
   
   **Advanced Settings:**
   - Plan: **Free** (750 hours/month)
   - Auto-Deploy: ✅ **Enabled**

### ⚙️ VAIHE 5: Environment Variables

Render Dashboardissa → Your Web Service → "Environment":

```bash
DATABASE_URL=postgresql://username:password@hostname:port/sentinel_100k
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
DEBUG=false
```

**Tietokannan URL**:
1. Mene tietokanta-serviceen
2. Kopioi "External Database URL"
3. Liitä se `DATABASE_URL` -muuttujaan

### 🎯 VAIHE 6: Deployment

1. **Deploy** → Render käynnistää automaattisesti
2. **Odota** 5-10 minuuttia buildille
3. **Tarkista** deployment log:
   ```
   ✅ Sentinel 100K starting in production mode
   ✅ Database: postgresql://...
   ✅ Sentinel 100K production ready!
   ```

### 🌟 VAIHE 7: Testaus

**Live URL**: `https://sentinel-100k.onrender.com`

**Testaa endpoints**:
```bash
# Health check
curl https://sentinel-100k.onrender.com/health

# API Documentation
https://sentinel-100k.onrender.com/docs

# Start onboarding
curl -X POST https://sentinel-100k.onrender.com/api/v1/onboarding/start
```

## 🎯 OMINAISUUDET RENDERISSÄ

### ✅ Mukana olevat palvelut:
- **Deep Onboarding** (Syvä käyttöönotto)
- **7-Week Cycles** (7-viikon syklit)
- **Night Analysis** (Yöanalyysi)
- **AI Chat** (Suomenkielinen tekoäly)
- **PostgreSQL Database** (Pilvitietokanta)
- **Automatic Backups** (Automaattiset varmuuskopiot)

### 📊 Renderiin optimoitu:
- **Production-ready** konfiguraatio
- **PostgreSQL** -tuki
- **Environment variables** -hallinta
- **CORS** production-asetukset
- **Error handling** parannettu
- **Logging** optimoitu

## 🔧 YLLÄPITO JA PÄIVITYKSET

### 🔄 Automaattiset deploymentit:
1. **Muokkaa koodia** paikallisesti
2. **Commit & push** GitHubiin:
   ```bash
   git add .
   git commit -m "Update features"
   git push
   ```
3. **Render** deployaa automaattisesti uuden version

### 📈 Monitorointi:
- **Logs**: Render Dashboard → Service → Logs
- **Metrics**: CPU, Memory, Response times
- **Uptime**: 99.9% SLA ilmaisessa planissa

### 🔄 Skalaus:
- **Free Plan**: 0.1 CPU, 512MB RAM
- **Paid Plans**: Enemmän resursseja tarpeen mukaan

## 🎯 KUSTOMOINTI

### 🎨 Domain:
1. **Custom Domain** → Renderissä
2. **SSL** automaattisesti mukana
3. **Esim**: `sentinel100k.fi`

### 📧 Notifications:
Render → Service Settings → Deploy Notifications:
- **Slack**
- **Discord** 
- **Email**

## 🛡️ TURVALLISUUS

### 🔐 Automaattisesti mukana:
- **SSL/TLS** encryption
- **Environment variables** salattu
- **Database** salaus
- **DDoS** suojaus
- **Automatic security updates**

### 🔑 Recommended:
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📱 KÄYTTÖ PRODUCTION-YMPÄRISTÖSSÄ

### 🌐 Live URLs:
- **Frontend**: `https://sentinel-100k.onrender.com`
- **API Docs**: `https://sentinel-100k.onrender.com/docs`
- **Health**: `https://sentinel-100k.onrender.com/health`

### 🎯 API Endpoints:
```bash
POST /api/v1/onboarding/start     # Aloita onboarding
POST /api/v1/onboarding/complete  # Viimeistele onboarding
GET  /api/v1/cycles/current/{id}  # Nykyinen viikkosykli
POST /api/v1/chat/complete        # AI-chat suomeksi
GET  /api/v1/analysis/night/latest # Viimeisin yöanalyysi
```

## 🎉 VALMIS!

**Sentinel 100K on nyt live Renderissä!**

🔥 **ILMAINEN**: 750 tuntia/kuukausi
🚀 **NOPEA**: Automaattiset deploymentit
💾 **VARMA**: PostgreSQL + varmuuskopiot
🌍 **GLOBAALI**: CDN + SSL mukana

**Live Demo**: https://sentinel-100k.onrender.com

---

## 🆘 TROUBLESHOOTING

### ❌ Build epäonnistuu:
```bash
# Tarkista requirements.txt
pip install -r requirements.txt

# Tarkista Python-versio
python --version  # Pitää olla 3.9+
```

### ❌ Database connection fails:
1. Tarkista `DATABASE_URL` environment variable
2. Varmista että PostgreSQL service on running
3. Kokeile connection manuaalisesti

### ❌ 503 Service Unavailable:
1. Tarkista deployment logs
2. Varmista että start command on oikein
3. Tarkista että port on `$PORT`

**Tuki**: render-community.slack.com 