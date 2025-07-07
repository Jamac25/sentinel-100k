# 🚀 Sentinel 100K - Käyttöönotto-ohje

## 📋 Sisällysluettelo

- [Yleiskatsaus](#yleiskatsaus)
- [Järjestelmävaatimukset](#järjestelmävaatimukset)
- [Asennus](#asennus)
- [Konfiguraatio](#konfiguraatio)
- [Tietokanta](#tietokanta)
- [AI-palvelut](#ai-palvelut)
- [Turvallisuus](#turvallisuus)
- [Käyttöönotto](#käyttöönotto)
- [Seuranta](#seuranta)
- [Varmuuskopiointi](#varmuuskopiointi)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Yleiskatsaus

Tämä ohje kattaa Sentinel 100K -järjestelmän täydellisen käyttöönoton tuotantoympäristöön. Järjestelmä koostuu 16 eri palvelusta, jotka kaikki tarvitsevat oman konfiguraationsa.

### 📊 Järjestelmän komponentit
- **Backend API**: FastAPI-pohjainen REST API
- **Frontend**: Streamlit-pohjainen käyttöliittymä
- **Tietokanta**: SQLite (kehitys) / PostgreSQL (tuotanto)
- **AI-palvelut**: OpenAI, Google Vision, paikalliset ML-mallit
- **Automaatio**: Taustaprosessit ja ajastukset
- **Turvallisuus**: JWT, salaus, audit logging

---

## 💻 Järjestelmävaatimukset

### Minimivaatimukset
- **CPU**: 4 ydin (8 ydin suositeltu)
- **RAM**: 8 GB (16 GB suositeltu)
- **Tallennustila**: 50 GB vapaata tilaa
- **OS**: Linux (Ubuntu 20.04+), macOS 12+, Windows 10+
- **Python**: 3.9+ (3.11 suositeltu)

### Suositusvaatimukset (tuotanto)
- **CPU**: 8+ ydin
- **RAM**: 32 GB
- **Tallennustila**: 200 GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **GPU**: NVIDIA RTX 3060+ (AI-mallien koulutukseen)

### Verkkovaatimukset
- **Kaistanleveys**: 100 Mbps (1 Gbps suositeltu)
- **Latenssi**: < 50ms OpenAI API:in
- **SSL**: Let's Encrypt tai vastaava
- **DNS**: A- ja CNAME-tietueet

---

## 📦 Asennus

### 1. Ympäristön valmistelu

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y tesseract-ocr tesseract-ocr-fin
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx redis-server

# macOS
brew install python@3.11
brew install tesseract tesseract-lang
brew install postgresql redis

# Windows
# Lataa Python 3.11 python.org:sta
# Asenna Tesseract OCR
# Asenna PostgreSQL
```

### 2. Projektin kloonaus

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
pip install -r requirements-dev.txt  # Kehitystyökalut
```

### 3. Ympäristömuuttujat

```bash
# Luo .env tiedosto
cp .env.example .env

# Muokkaa .env tiedostoa
nano .env
```

```env
# Perusasetukset
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/sentinel_db

# AI-palvelut
OPENAI_API_KEY=sk-your-openai-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-credentials.json

# OCR-palvelut
TESSERACT_PATH=/usr/bin/tesseract
OCR_LANGUAGE=fin+eng

# Tietoturva
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Tiedostojen käsittely
UPLOAD_DIR=/var/sentinel/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# Lokitus
LOG_LEVEL=INFO
LOG_FILE=/var/log/sentinel/app.log
ERROR_LOG_FILE=/var/log/sentinel/errors.log

# Redis
REDIS_URL=redis://localhost:6379

# Sähköposti
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Seuranta
SENTRY_DSN=your-sentry-dsn
```

---

## ⚙️ Konfiguraatio

### 1. Tietokanta

```bash
# PostgreSQL asennus ja konfiguraatio
sudo -u postgres createuser sentinel_user
sudo -u postgres createdb sentinel_db
sudo -u postgres psql -c "ALTER USER sentinel_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sentinel_db TO sentinel_user;"

# Tietokannan alustus
python -m app.db.init_db
```

### 2. Redis

```bash
# Redis konfiguraatio
sudo nano /etc/redis/redis.conf

# Lisää seuraavat asetukset:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Käynnistä Redis
sudo systemctl restart redis
sudo systemctl enable redis
```

### 3. Nginx

```bash
# Nginx konfiguraatio
sudo nano /etc/nginx/sites-available/sentinel

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Tiedostojen lataus
    location /uploads/ {
        alias /var/sentinel/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Ota konfiguraatio käyttöön
sudo ln -s /etc/nginx/sites-available/sentinel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. SSL-sertifikaatti

```bash
# Let's Encrypt asennus
sudo apt install certbot python3-certbot-nginx

# Sertifikaatin hankinta
sudo certbot --nginx -d your-domain.com

# Automaattinen uusinta
sudo crontab -e
# Lisää: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🤖 AI-palvelut

### 1. OpenAI API

```bash
# API-avaimen asetus
export OPENAI_API_KEY="sk-your-api-key"

# Testaa yhteys
python -c "
import openai
openai.api_key = 'sk-your-api-key'
response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Test'}]
)
print('OpenAI API toimii!')
"
```

### 2. Google Vision API

```bash
# Lataa credentials.json Google Cloud Console:sta
# Aseta polku ympäristömuuttujaan
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# Testaa yhteys
python -c "
from google.cloud import vision
client = vision.ImageAnnotatorClient()
print('Google Vision API toimii!')
"
```

### 3. Paikalliset ML-mallit

```bash
# Asenna scikit-learn ja muut ML-kirjastot
pip install scikit-learn pandas numpy matplotlib seaborn

# Kouluta kategorisointimalli
python -m app.services.categorization_service --train

# Testaa malli
python -c "
from app.services.categorization_service import TransactionCategorizationService
service = TransactionCategorizationService()
result = service.predict_category('K-Market ruokaostokset', 45.67)
print(f'Kategoria: {result}')
"
```

---

## 🔒 Turvallisuus

### 1. Palomuurin konfiguraatio

```bash
# UFW palomuurin asennus
sudo apt install ufw

# Perusasetukset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Ota palomuuri käyttöön
sudo ufw enable
sudo ufw status
```

### 2. Salasanan vahvuus

```bash
# Salasanan vahvuuden testaus
python -c "
from app.services.auth_service import AuthService
auth = AuthService()
strength = auth.check_password_strength('TestPassword123!')
print(f'Salasanan vahvuus: {strength}')
"
```

### 3. Audit logging

```bash
# Audit logien konfiguraatio
sudo mkdir -p /var/log/sentinel/audit
sudo chown -R sentinel:sentinel /var/log/sentinel

# Testaa audit logging
python -c "
from app.services.auth_service import AuthService
auth = AuthService()
auth.log_security_event('test_login', {'user_id': 1, 'ip': '127.0.0.1'})
print('Audit logging toimii!')
"
```

---

## 🚀 Käyttöönotto

### 1. Systemd palvelut

```bash
# Luo systemd palvelut
sudo nano /etc/systemd/system/sentinel-api.service

[Unit]
Description=Sentinel 100K API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=sentinel
Group=sentinel
WorkingDirectory=/opt/sentinel-100k
Environment=PATH=/opt/sentinel-100k/venv/bin
ExecStart=/opt/sentinel-100k/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Frontend palvelu
sudo nano /etc/systemd/system/sentinel-frontend.service

[Unit]
Description=Sentinel 100K Frontend
After=network.target sentinel-api.service

[Service]
Type=exec
User=sentinel
Group=sentinel
WorkingDirectory=/opt/sentinel-100k
Environment=PATH=/opt/sentinel-100k/venv/bin
ExecStart=/opt/sentinel-100k/venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Taustaprosessit
sudo nano /etc/systemd/system/sentinel-worker.service

[Unit]
Description=Sentinel 100K Background Worker
After=network.target sentinel-api.service

[Service]
Type=exec
User=sentinel
Group=sentinel
WorkingDirectory=/opt/sentinel-100k
Environment=PATH=/opt/sentinel-100k/venv/bin
ExecStart=/opt/sentinel-100k/venv/bin/python -m app.services.scheduler_service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Palveluiden käynnistys

```bash
# Ota palvelut käyttöön
sudo systemctl daemon-reload
sudo systemctl enable sentinel-api
sudo systemctl enable sentinel-frontend
sudo systemctl enable sentinel-worker

# Käynnistä palvelut
sudo systemctl start sentinel-api
sudo systemctl start sentinel-frontend
sudo systemctl start sentinel-worker

# Tarkista tila
sudo systemctl status sentinel-api
sudo systemctl status sentinel-frontend
sudo systemctl status sentinel-worker
```

### 3. Docker käyttöönotto (vaihtoehto)

```bash
# Docker Compose asennus
sudo apt install docker.io docker-compose

# Käyttäjän lisäys docker-ryhmään
sudo usermod -aG docker $USER

# Docker Compose tiedosto
cat > docker-compose.yml << EOF
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/sentinel_db
    depends_on:
      - db
      - redis

  frontend:
    build: .
    command: streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    depends_on:
      - api

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: sentinel_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
EOF

# Käynnistä Docker Compose
docker-compose up -d
```

---

## 📊 Seuranta

### 1. Logien seuranta

```bash
# Reaaliaikainen logien seuranta
sudo journalctl -u sentinel-api -f
sudo journalctl -u sentinel-frontend -f
sudo journalctl -u sentinel-worker -f

# Sovelluksen logit
tail -f /var/log/sentinel/app.log
tail -f /var/log/sentinel/errors.log
```

### 2. Suorituskyvyn seuranta

```bash
# Järjestelmän resurssit
htop
iotop
nethogs

# Tietokannan suorituskyky
sudo -u postgres psql -d sentinel_db -c "
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE schemaname = 'public';
"
```

### 3. Verkkoliikenteen seuranta

```bash
# Nginx logien analyysi
sudo tail -f /var/log/nginx/access.log | grep sentinel

# API endpointien suorituskyky
curl -w "@curl-format.txt" -o /dev/null -s "https://your-domain.com/api/v1/dashboard/summary"
```

---

## 💾 Varmuuskopiointi

### 1. Tietokannan varmuuskopiointi

```bash
# Automaattinen varmuuskopiointi
sudo nano /opt/sentinel-100k/scripts/backup.sh

#!/bin/bash
BACKUP_DIR="/var/backups/sentinel"
DATE=$(date +%Y%m%d_%H%M%S)

# Tietokannan varmuuskopiointi
pg_dump -h localhost -U sentinel_user sentinel_db > $BACKUP_DIR/db_backup_$DATE.sql

# Tiedostojen varmuuskopiointi
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /var/sentinel/uploads/

# Vanhojen varmuuskopioiden poisto (30 päivää)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Varmuuskopiointi valmis: $DATE"
```

```bash
# Tee skriptistä suoritettava
chmod +x /opt/sentinel-100k/scripts/backup.sh

# Lisää cron-ajastus
sudo crontab -e
# Lisää: 0 2 * * * /opt/sentinel-100k/scripts/backup.sh
```

### 2. Palautus

```bash
# Tietokannan palautus
psql -h localhost -U sentinel_user sentinel_db < backup_file.sql

# Tiedostojen palautus
tar -xzf files_backup.tar.gz -C /
```

---

## 🔧 Troubleshooting

### Yleisimmät ongelmat

#### 1. API ei vastaa
```bash
# Tarkista palvelun tila
sudo systemctl status sentinel-api

# Tarkista portit
sudo netstat -tlnp | grep 8000

# Tarkista logit
sudo journalctl -u sentinel-api --no-pager -n 50
```

#### 2. Tietokantayhteys
```bash
# Testaa yhteys
psql -h localhost -U sentinel_user -d sentinel_db -c "SELECT 1;"

# Tarkista PostgreSQL
sudo systemctl status postgresql

# Tarkista ympäristömuuttujat
echo $DATABASE_URL
```

#### 3. AI-palvelut eivät toimi
```bash
# Testaa OpenAI API
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Testaa Google Vision
python -c "
from google.cloud import vision
client = vision.ImageAnnotatorClient()
print('Google Vision toimii')
"
```

#### 4. Muistin loppuminen
```bash
# Tarkista muistin käyttö
free -h

# Tarkista swap
swapon --show

# Lisää swap-tiedosto
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Debug-tila

```bash
# Ota debug-tila käyttöön
export DEBUG=true
export LOG_LEVEL=DEBUG

# Käynnistä palvelut uudelleen
sudo systemctl restart sentinel-api
sudo systemctl restart sentinel-frontend
```

---

## 📞 Tuki

### Hyödyllisiä komentoja

```bash
# Järjestelmän tila
sudo systemctl status sentinel-*

# Logien tarkastelu
sudo journalctl -u sentinel-api --since "1 hour ago"

# Tietokannan koko
sudo -u postgres psql -d sentinel_db -c "
SELECT pg_size_pretty(pg_database_size('sentinel_db'));
"

# Aktiiviset yhteydet
sudo netstat -tlnp | grep sentinel

# Disk-käyttö
df -h /var/sentinel/
```

### Yhteystiedot

- **Tekninen tuki**: tech-support@sentinel-100k.com
- **Dokumentaatio**: https://docs.sentinel-100k.com
- **GitHub Issues**: https://github.com/your-org/sentinel-100k/issues
- **Discord**: https://discord.gg/sentinel-100k

---

**Luotu**: Sentinel 100K Development Team  
**Versio**: 1.0.0  
**Päivitetty**: 2024-01-15  
**Status**: Production Ready ✅ 