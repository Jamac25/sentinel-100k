# 🌐 Sentinel 100K - API Dokumentaatio

## 📋 Sisällysluettelo

- [Yleiskatsaus](#yleiskatsaus)
- [Autentikointi](#autentikointi)
- [Autentikointi API](#autentikointi-api)
- [Transaktiot API](#transaktiot-api)
- [Kategoriat API](#kategoriat-api)
- [Dashboard API](#dashboard-api)
- [Dokumentit API](#dokumentit-api)
- [Intelligence API](#intelligence-api)
- [Watchdog API](#watchdog-api)
- [Guardian API](#guardian-api)
- [Virheenkäsittely](#virheenkäsittely)
- [Rate Limiting](#rate-limiting)

---

## 🎯 Yleiskatsaus

Sentinel 100K API tarjoaa 50+ endpointia, jotka kattavat kaikki henkilökohtaisen rahoituksen tarpeet. API on RESTful-pohjainen ja käyttää JSON-muotoa datan vaihtoon.

### Base URL
```
Development: http://localhost:8000
Production: https://sentinel-100k.onrender.com
```

### Content-Type
Kaikki pyynnöt käyttävät `application/json` content-typea.

### Vastauskoodit
- `200` - Onnistunut
- `201` - Luotu
- `400` - Virheellinen pyyntö
- `401` - Ei autentikointia
- `403` - Ei oikeuksia
- `404` - Ei löytynyt
- `422` - Validointivirhe
- `500` - Palvelinvirhe

---

## 🔐 Autentikointi

### JWT Token
Kaikki endpointit (paitsi `/auth/register` ja `/auth/login`) vaativat JWT token -autentikoinnin.

```bash
Authorization: Bearer <your-jwt-token>
```

### Token rakenne
```json
{
  "sub": "user@example.com",
  "exp": 1642234567,
  "iat": 1642230967,
  "type": "access"
}
```

### Token vanhentuminen
- **Access Token**: 30 minuuttia
- **Refresh Token**: 7 päivää

---

## 🔐 Autentikointi API

### POST /api/v1/auth/register
Käyttäjän rekisteröityminen.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "Test User",
  "password": "SecurePass123!"
}
```

**Vastaus (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "Test User",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Virhe (400):**
```json
{
  "detail": "Käyttäjä on jo olemassa"
}
```

### POST /api/v1/auth/login
Käyttäjän kirjautuminen.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Vastaus (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "Test User"
  }
}
```

**Virhe (401):**
```json
{
  "detail": "Virheellinen sähköposti tai salasana"
}
```

### POST /api/v1/auth/refresh
Token päivitys.

**Headers:**
```bash
Authorization: Bearer <current-token>
```

**Vastaus (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### GET /api/v1/auth/me
Käyttäjän tiedot.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "Test User",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### POST /api/v1/auth/logout
Kirjautuminen ulos.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "message": "Successfully logged out"
}
```

### POST /api/v1/auth/change-password
Salasanan vaihto.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

**Vastaus (200):**
```json
{
  "message": "Password changed successfully"
}
```

---

## 💰 Transaktiot API

### POST /api/v1/transactions/
Uuden transaktion luominen.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "description": "K-Market ruokaostokset",
  "amount": 45.67,
  "category": "ruoka",
  "date": "2024-01-15",
  "type": "expense"
}
```

**Vastaus (201):**
```json
{
  "id": 123,
  "description": "K-Market ruokaostokset",
  "amount": 45.67,
  "category": "ruoka",
  "date": "2024-01-15",
  "type": "expense",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET /api/v1/transactions/
Transaktioiden listaus.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Limit (default: 100, max: 1000)
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `category`: Category filter
- `type`: Transaction type (income/expense)
- `min_amount`: Minimum amount
- `max_amount`: Maximum amount
- `search`: Text search in description

**Esimerkki:**
```bash
GET /api/v1/transactions/?start_date=2024-01-01&category=ruoka&limit=50
```

**Vastaus (200):**
```json
{
  "transactions": [
    {
      "id": 123,
      "description": "K-Market ruokaostokset",
      "amount": 45.67,
      "category": "ruoka",
      "date": "2024-01-15",
      "type": "expense",
      "user_id": 1,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100,
  "has_more": false
}
```

### GET /api/v1/transactions/{id}
Yksittäisen transaktion haku.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "id": 123,
  "description": "K-Market ruokaostokset",
  "amount": 45.67,
  "category": "ruoka",
  "date": "2024-01-15",
  "type": "expense",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### PUT /api/v1/transactions/{id}
Transaktion päivitys.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "description": "K-Market ruokaostokset päivitetty",
  "amount": 50.00,
  "category": "ruoka"
}
```

**Vastaus (200):**
```json
{
  "id": 123,
  "description": "K-Market ruokaostokset päivitetty",
  "amount": 50.00,
  "category": "ruoka",
  "date": "2024-01-15",
  "type": "expense",
  "user_id": 1,
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### DELETE /api/v1/transactions/{id}
Transaktion poisto.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (204):**
```json
{}
```

### GET /api/v1/transactions/stats
Transaktioiden tilastot.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `group_by`: Grouping (day/week/month/category)

**Vastaus (200):**
```json
{
  "total_income": 5000.00,
  "total_expenses": 3000.00,
  "net_amount": 2000.00,
  "transaction_count": 150,
  "average_transaction": 53.33,
  "category_breakdown": {
    "ruoka": {
      "total": 800.00,
      "count": 45,
      "average": 17.78,
      "percentage": 26.67
    },
    "kuljetus": {
      "total": 400.00,
      "count": 20,
      "average": 20.00,
      "percentage": 13.33
    }
  },
  "monthly_trends": [
    {
      "month": "2024-01",
      "income": 5000.00,
      "expenses": 3000.00,
      "net": 2000.00
    }
  ],
  "daily_averages": {
    "income": 166.67,
    "expenses": 100.00,
    "net": 66.67
  }
}
```

### POST /api/v1/transactions/bulk
Useiden transaktioiden luominen.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "transactions": [
    {
      "description": "K-Market ruokaostokset",
      "amount": 45.67,
      "category": "ruoka",
      "date": "2024-01-15"
    },
    {
      "description": "Bussilippu",
      "amount": 3.50,
      "category": "kuljetus",
      "date": "2024-01-15"
    }
  ]
}
```

**Vastaus (201):**
```json
{
  "created": 2,
  "failed": 0,
  "transactions": [
    {
      "id": 123,
      "description": "K-Market ruokaostokset",
      "amount": 45.67,
      "category": "ruoka",
      "date": "2024-01-15"
    },
    {
      "id": 124,
      "description": "Bussilippu",
      "amount": 3.50,
      "category": "kuljetus",
      "date": "2024-01-15"
    }
  ]
}
```

---

## 🏷️ Kategoriat API

### GET /api/v1/categories/
Kategorioiden listaus.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "ruoka",
      "description": "Ruokaostokset",
      "color": "#FF6B6B",
      "icon": "🍽️",
      "transaction_count": 45,
      "total_amount": 800.00,
      "average_amount": 17.78
    },
    {
      "id": 2,
      "name": "kuljetus",
      "description": "Kuljetuskulut",
      "color": "#4ECDC4",
      "icon": "🚌",
      "transaction_count": 20,
      "total_amount": 400.00,
      "average_amount": 20.00
    }
  ]
}
```

### POST /api/v1/categories/predict
Kategorian ennustus.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "description": "K-Market ruokaostokset",
  "amount": 45.67
}
```

**Vastaus (200):**
```json
{
  "predicted_category": "ruoka",
  "confidence": 0.95,
  "alternative_categories": [
    {
      "category": "viihde",
      "confidence": 0.03
    },
    {
      "category": "kuljetus",
      "confidence": 0.02
    }
  ],
  "reasoning": "K-Market on ruokakauppa, joten kategoria on todennäköisesti 'ruoka'"
}
```

### PUT /api/v1/categories/correct
Kategorian korjaus.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "transaction_id": 123,
  "correct_category": "viihde",
  "confidence": 0.95
}
```

**Vastaus (200):**
```json
{
  "message": "Category corrected successfully",
  "transaction_id": 123,
  "new_category": "viihde",
  "learning_applied": true
}
```

### GET /api/v1/categories/stats
Kategorioiden tilastot.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `type`: Transaction type (income/expense)

**Vastaus (200):**
```json
{
  "category_stats": [
    {
      "category": "ruoka",
      "total_amount": 800.00,
      "transaction_count": 45,
      "average_amount": 17.78,
      "percentage": 26.67,
      "trend": "increasing",
      "trend_percentage": 15.2
    }
  ],
  "total_transactions": 150,
  "total_amount": 3000.00,
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

### GET /api/v1/categories/usage
Kategorioiden käyttötilastot.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "most_used_categories": [
    {
      "category": "ruoka",
      "usage_count": 45,
      "last_used": "2024-01-15T10:30:00Z"
    }
  ],
  "least_used_categories": [
    {
      "category": "koulutus",
      "usage_count": 2,
      "last_used": "2024-01-10T14:20:00Z"
    }
  ],
  "accuracy_stats": {
    "total_predictions": 150,
    "correct_predictions": 135,
    "accuracy_percentage": 90.0
  }
}
```

---

## 📊 Dashboard API

### GET /api/v1/dashboard/summary
Taloudellinen yhteenveto.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "current_balance": 15000.00,
  "monthly_income": 5000.00,
  "monthly_expenses": 3000.00,
  "savings_rate": 40.0,
  "goal_progress": 15.0,
  "goal_amount": 100000.00,
  "savings_to_date": 15000.00,
  "top_categories": [
    {
      "category": "ruoka",
      "amount": 800.00,
      "percentage": 26.67,
      "trend": "increasing"
    }
  ],
  "recent_transactions": [
    {
      "id": 123,
      "description": "K-Market ruokaostokset",
      "amount": 45.67,
      "category": "ruoka",
      "date": "2024-01-15",
      "type": "expense"
    }
  ],
  "alerts": [
    {
      "type": "high_spending",
      "message": "Kulut ovat 20% korkeammat kuin viime kuussa",
      "severity": "warning",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

### GET /api/v1/dashboard/insights
Älykkäät oivallukset.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `insight_type`: Insight type (savings, spending, trends)
- `limit`: Number of insights (default: 5)

**Vastaus (200):**
```json
{
  "insights": [
    {
      "type": "savings_opportunity",
      "title": "Säästömahdollisuus havaittu",
      "message": "Voit säästää 200€/kk vähentämällä viihdekuluja",
      "impact": 200.00,
      "confidence": 0.85,
      "category": "viihde",
      "actionable": true,
      "priority": "high"
    },
    {
      "type": "spending_trend",
      "title": "Kulutrendi",
      "message": "Ruokakulut ovat nousseet 15% viime kuusta",
      "trend": "increasing",
      "percentage": 15.0,
      "category": "ruoka",
      "period": "monthly"
    }
  ],
  "recommendations": [
    {
      "action": "reduce_entertainment",
      "title": "Vähennä viihdekuluja",
      "description": "Voi säästää 150€/kk",
      "difficulty": "medium",
      "impact": 150.00,
      "implementation_time": "1-2 weeks"
    }
  ],
  "summary": {
    "total_insights": 5,
    "high_priority": 2,
    "total_savings_potential": 350.00
  }
}
```

### GET /api/v1/dashboard/charts
Kaaviodata.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `chart_type`: Chart type (expenses_by_category, monthly_trends, savings_progress)
- `period`: Time period (1m, 3m, 6m, 1y)

**Vastaus (200):**
```json
{
  "chart_type": "expenses_by_category",
  "data": {
    "labels": ["ruoka", "kuljetus", "viihde", "asuminen"],
    "datasets": [
      {
        "label": "Kulut (€)",
        "data": [800, 400, 300, 1200],
        "backgroundColor": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
      }
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false
  },
  "metadata": {
    "total_amount": 2700.00,
    "period": "2024-01-01 to 2024-01-31"
  }
}
```

### GET /api/v1/dashboard/goals
Tavoitteiden eteneminen.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "goals": [
    {
      "id": 1,
      "name": "100,000€ säästötavoite",
      "target_amount": 100000.00,
      "current_amount": 15000.00,
      "progress_percentage": 15.0,
      "target_date": "2027-12-31",
      "status": "active",
      "monthly_savings_needed": 2361.11,
      "projected_completion": "2027-06-15",
      "milestones": [
        {
          "milestone": "25%",
          "amount": 25000.00,
          "achieved": false,
          "projected_date": "2025-03-15"
        }
      ]
    }
  ],
  "summary": {
    "total_goals": 1,
    "active_goals": 1,
    "completed_goals": 0,
    "total_progress": 15.0
  }
}
```

---

## 📄 Dokumentit API

### POST /api/v1/documents/upload
Dokumentin lataus.

**Headers:**
```bash
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: File to upload (PDF, JPG, PNG, max 10MB)
- `description`: Optional description
- `category`: Optional category hint

**Vastaus (201):**
```json
{
  "id": 456,
  "filename": "receipt.jpg",
  "file_size": 1024000,
  "mime_type": "image/jpeg",
  "description": "K-Market kuitti",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "processing_status": "pending",
  "ocr_text": null,
  "extracted_data": null
}
```

### GET /api/v1/documents/
Dokumenttien listaus.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Limit (default: 100)
- `status`: Processing status (pending, processed, failed)
- `mime_type`: File type filter
- `start_date`: Upload start date
- `end_date`: Upload end date

**Vastaus (200):**
```json
{
  "documents": [
    {
      "id": 456,
      "filename": "receipt.jpg",
      "file_size": 1024000,
      "mime_type": "image/jpeg",
      "description": "K-Market kuitti",
      "uploaded_at": "2024-01-15T10:30:00Z",
      "processing_status": "processed",
      "ocr_text": "K-Market 45.67€ 15.1.2024",
      "extracted_data": {
        "merchant": "K-Market",
        "amount": 45.67,
        "date": "2024-01-15",
        "items": ["ruoka", "juomat"]
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100,
  "has_more": false
}
```

### GET /api/v1/documents/{id}
Dokumentin haku.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "id": 456,
  "filename": "receipt.jpg",
  "file_size": 1024000,
  "mime_type": "image/jpeg",
  "description": "K-Market kuitti",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "processing_status": "processed",
  "ocr_text": "K-Market 45.67€ 15.1.2024",
  "extracted_data": {
    "merchant": "K-Market",
    "amount": 45.67,
    "date": "2024-01-15",
    "items": ["ruoka", "juomat"]
  },
  "file_url": "https://your-app.com/uploads/receipt.jpg",
  "processing_time": 2.5
}
```

### DELETE /api/v1/documents/{id}
Dokumentin poisto.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (204):**
```json
{}
```

### POST /api/v1/documents/{id}/process
Dokumentin käsittely.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "message": "Document processing started",
  "document_id": 456,
  "estimated_time": 5
}
```

### GET /api/v1/documents/{id}/text
Dokumentin teksti.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "document_id": 456,
  "ocr_text": "K-Market 45.67€ 15.1.2024",
  "confidence": 0.95,
  "language": "fi",
  "processing_time": 2.5
}
```

---

## 🤖 Intelligence API

### POST /api/v1/intelligence/chat
AI-keskustelu.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "message": "Miten voin säästää enemmän?",
  "context": "user_financial_data",
  "conversation_id": "conv_123"
}
```

**Vastaus (200):**
```json
{
  "response": "Analysoin kulutustottumuksesi ja huomaan, että voit säästää 200€/kk vähentämällä viihdekuluja. Suosittelen myös ruokakauppojen suunnittelua etukäteen.",
  "suggestions": [
    "Vähennä viihdekuluja 150€/kk",
    "Suunnittele ruokaostokset etukäteen",
    "Käytä kuponkeja ja tarjouksia"
  ],
  "confidence": 0.85,
  "conversation_id": "conv_123",
  "tokens_used": 150,
  "response_time": 2.3
}
```

### GET /api/v1/intelligence/ideas
Säästöideoiden generointi.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit`: Number of ideas (default: 5)
- `category`: Specific category focus
- `difficulty`: Difficulty level (easy, medium, hard)

**Vastaus (200):**
```json
{
  "ideas": [
    {
      "id": 789,
      "title": "Vähennä viihdekuluja",
      "description": "Voit säästää 150€/kk vähentämällä viihdekuluja 30%",
      "potential_savings": 150.00,
      "difficulty": "medium",
      "implementation_time": "1-2 viikkoa",
      "category": "viihde",
      "steps": [
        "Analysoi nykyiset viihdekulut",
        "Aseta kuukausittainen budjetti",
        "Etsi ilmaisia vaihtoehtoja"
      ],
      "success_rate": 0.75
    }
  ],
  "total_potential_savings": 300.00,
  "generation_time": 1.2
}
```

### POST /api/v1/intelligence/analyze
Syvällinen talousanalyysi.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "analysis_type": "comprehensive",
  "timeframe": "6m",
  "include_predictions": true
}
```

**Vastaus (200):**
```json
{
  "analysis": {
    "spending_patterns": {
      "trend": "increasing",
      "rate": 5.2,
      "main_drivers": ["ruoka", "kuljetus"],
      "seasonality": "monthly"
    },
    "savings_potential": {
      "immediate": 200.00,
      "short_term": 500.00,
      "long_term": 1500.00,
      "categories": {
        "viihde": 150.00,
        "ruoka": 100.00,
        "kuljetus": 50.00
      }
    },
    "risk_factors": [
      {
        "factor": "high_entertainment_spending",
        "severity": "medium",
        "impact": 300.00,
        "mitigation": "Set monthly budget"
      }
    ],
    "predictions": {
      "next_month_expenses": 3200.00,
      "savings_rate_6m": 35.0,
      "goal_completion_date": "2027-06-15"
    }
  },
  "recommendations": [
    {
      "priority": "high",
      "action": "reduce_entertainment",
      "impact": 200.00,
      "timeline": "1 month",
      "difficulty": "medium"
    }
  ],
  "analysis_time": 3.5
}
```

### GET /api/v1/intelligence/insights
AI-pohjaiset oivallukset.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `insight_type`: Type of insights (spending, saving, behavior)
- `limit`: Number of insights (default: 10)

**Vastaus (200):**
```json
{
  "insights": [
    {
      "id": "insight_123",
      "type": "spending_anomaly",
      "title": "Poikkeuksellinen kulutus havaittu",
      "message": "Viihdekulut ovat 50% korkeammat kuin normaalisti tässä kuussa",
      "severity": "high",
      "category": "viihde",
      "data": {
        "current": 450.00,
        "average": 300.00,
        "increase": 50.0
      },
      "recommendation": "Tarkista viihdekulut ja aseta budjetti",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "summary": {
    "total_insights": 5,
    "high_severity": 2,
    "medium_severity": 2,
    "low_severity": 1
  }
}
```

---

## 🚨 Watchdog API

### GET /api/v1/watchdog/status
Watchdog tilan tarkistus.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "status": "active",
  "last_check": "2024-01-15T10:30:00Z",
  "active_alerts": 2,
  "monitoring_metrics": {
    "spending_trend": "stable",
    "savings_rate": "on_track",
    "anomaly_count": 1,
    "risk_level": "medium"
  },
  "system_health": {
    "database": "healthy",
    "ai_services": "healthy",
    "ocr_service": "healthy"
  }
}
```

### GET /api/v1/watchdog/alerts
Aktiivisten hälytysten listaus.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `severity`: Alert severity (low, medium, high, critical)
- `status`: Alert status (active, acknowledged, resolved)
- `limit`: Number of alerts (default: 50)

**Vastaus (200):**
```json
{
  "alerts": [
    {
      "id": 123,
      "type": "high_spending",
      "title": "Korkeat kulut havaittu",
      "message": "Tämän kuun kulut ovat 20% korkeammat kuin viime kuussa",
      "severity": "warning",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "acknowledged_at": null,
      "resolved_at": null,
      "data": {
        "current_spending": 3500.00,
        "previous_spending": 2900.00,
        "increase_percentage": 20.7,
        "affected_categories": ["viihde", "ruoka"]
      },
      "recommendations": [
        "Tarkista viihdekulut",
        "Aseta kuukausittainen budjetti"
      ]
    }
  ],
  "total": 2,
  "unacknowledged": 1,
  "summary": {
    "critical": 0,
    "high": 1,
    "medium": 1,
    "low": 0
  }
}
```

### POST /api/v1/watchdog/acknowledge/{alert_id}
Hälytyksen käsittely.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "action": "acknowledge",
  "notes": "Tarkistan kulut ja asetan budjetin"
}
```

**Vastaus (200):**
```json
{
  "message": "Alert acknowledged successfully",
  "alert_id": 123,
  "acknowledged_at": "2024-01-15T11:00:00Z"
}
```

### GET /api/v1/watchdog/analytics
Watchdog analytiikka.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `period`: Time period (1w, 1m, 3m, 6m)

**Vastaus (200):**
```json
{
  "alert_statistics": {
    "total_alerts": 25,
    "resolved_alerts": 20,
    "active_alerts": 5,
    "average_resolution_time": "2.5 days"
  },
  "alert_types": {
    "high_spending": 10,
    "savings_goal_at_risk": 5,
    "anomaly_detected": 8,
    "budget_exceeded": 2
  },
  "severity_distribution": {
    "critical": 2,
    "high": 8,
    "medium": 10,
    "low": 5
  },
  "trends": {
    "alerts_per_month": [5, 8, 12, 10],
    "resolution_rate": 0.8,
    "average_severity": "medium"
  }
}
```

---

## 👮 Guardian API

### GET /api/v1/guardian/users
Käyttäjien valvonta.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Vastaus (200):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "Test User",
      "status": "active",
      "last_login": "2024-01-15T10:30:00Z",
      "login_count": 45,
      "risk_score": 0.1
    }
  ],
  "total": 1,
  "active_users": 1,
  "suspended_users": 0
}
```

### POST /api/v1/guardian/restrictions
Rajoituksen lisäys.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "user_id": 1,
  "restriction_type": "spending_limit",
  "value": 1000,
  "reason": "High spending detected",
  "duration": "30d"
}
```

**Vastaus (200):**
```json
{
  "message": "Restriction added successfully",
  "restriction_id": 456,
  "applied_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-02-14T10:30:00Z"
}
```

### GET /api/v1/guardian/reports
Turvallisuusraportit.

**Headers:**
```bash
Authorization: Bearer <token>
```

**Query Parameters:**
- `report_type`: Report type (security, activity, compliance)
- `start_date`: Start date
- `end_date`: End date

**Vastaus (200):**
```json
{
  "report": {
    "type": "security",
    "period": "2024-01-01 to 2024-01-31",
    "summary": {
      "total_logins": 150,
      "failed_logins": 5,
      "suspicious_activities": 2,
      "security_incidents": 0
    },
    "details": [
      {
        "event": "failed_login",
        "timestamp": "2024-01-15T10:30:00Z",
        "user_id": 1,
        "ip_address": "192.168.1.100",
        "severity": "low"
      }
    ],
    "recommendations": [
      "Enable two-factor authentication",
      "Review failed login attempts"
    ]
  }
}
```

---

## 🚨 Virheenkäsittely

### Virhekoodit

#### 400 Bad Request
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_id": "abc123"
}
```

### Virheenkäsittely esimerkit

#### Token vanhentunut
```json
{
  "detail": "Token has expired",
  "code": "TOKEN_EXPIRED"
}
```

#### Rajoitus ylitetty
```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

#### Tietokantavirhe
```json
{
  "detail": "Database connection failed",
  "code": "DB_ERROR"
}
```

---

## ⚡ Rate Limiting

### Rajoitukset
- **Autentikoimattomat kutsut**: 10/minuutti
- **Autentikoidut kutsut**: 100/minuutti
- **AI palvelut**: 20/minuutti
- **Dokumenttien lataus**: 10/minuutti
- **Hälytykset**: 50/minuutti

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
Retry-After: 60
```

### Rate Limit vastaus
```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60,
  "limit": 100,
  "remaining": 0,
  "reset_time": 1642234567
}
```

---

## 🧪 Testaus

### Testausympäristö
```bash
# Testaus URL
http://localhost:8000/docs  # Swagger UI
http://localhost:8000/redoc # ReDoc
```

### Esimerkki testikutsut
```bash
# Rekisteröityminen
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPass123!"
  }'

# Kirjautuminen
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Transaktioiden haku (tokenilla)
curl -X GET "http://localhost:8000/api/v1/transactions/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Testikäyttäjät
```json
{
  "demo_user": {
    "email": "demo@example.com",
    "password": "DemoPass123"
  },
  "test_user": {
    "email": "test@example.com",
    "password": "TestPass123!"
  }
}
```

---

## 📞 Tuki

### Dokumentaatio
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

### Yhteyshenkilöt
- **API Support**: api-support@sentinel100k.com
- **Technical Issues**: tech-support@sentinel100k.com

---

**Luotu**: Sentinel 100K Development Team  
**Versio**: 1.0.0  
**Päivitetty**: 2024-01-15  
**Status**: Production Ready ✅ 