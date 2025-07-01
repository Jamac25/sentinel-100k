# 🚀 SENTINEL 100K - RENDER PIKAOPAS

## ⚡ 5 MINUUTISSA LIVENÄ!

### 1️⃣ GITHUB (1 min)
```bash
# Luo repo: https://github.com/new → sentinel-100k
git init
git add .
git commit -m "Sentinel 100K complete"
git remote add origin https://github.com/USERNAME/sentinel-100k.git
git push -u origin main
```

### 2️⃣ RENDER SETUP (2 min)
1. **Mene**: https://render.com → Sign up with GitHub
2. **PostgreSQL**: New → PostgreSQL → Name: `sentinel-db` → Plan: Free → Create
3. **Web Service**: New → Web Service → Connect `sentinel-100k` repo

### 3️⃣ SERVICE CONFIG (1 min)
```bash
Name: sentinel-100k
Build Command: pip install -r requirements.txt
Start Command: uvicorn sentinel_render_ready:app --host 0.0.0.0 --port $PORT
Plan: Free
```

### 4️⃣ ENVIRONMENT VARS (1 min)
```bash
DATABASE_URL = <copy from PostgreSQL service>
SECRET_KEY = _S8lH5WRlE5YbsgzVKZCxRKo6HrasTDOni1g9a8xGr8
ENVIRONMENT = production
DEBUG = false
```

### 5️⃣ DEPLOY & READY! ✅
- **Build time**: ~5 min
- **Live URL**: `https://sentinel-100k.onrender.com`
- **Test**: `https://sentinel-100k.onrender.com/health`

## 🎯 VALMIS!

**Sentinel 100K on nyt live internetissä!**
- 🌍 **Global access** (HTTPS + CDN)
- 🔒 **Secure** (PostgreSQL + SSL)
- ⚡ **Fast** (Edge locations)
- 💾 **Reliable** (Auto backups)

---

**Ongelmia?** Katso: `RENDER_DEPLOYMENT_GUIDE.md` 