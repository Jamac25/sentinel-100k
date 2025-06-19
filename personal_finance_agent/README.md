# Personal Finance Agent 🏦💰

AI-powered personal finance agent designed to help you save aggressively towards your €100,000 financial goal through automated budgeting, intelligent expense tracking, and personalized recommendations.

## 🎯 Project Overview

This application combines modern Python web technologies with AI/ML capabilities to create an emotionally engaging financial assistant that learns from your spending patterns and provides proactive guidance.

### Key Features

- **Automated Document Processing**: OCR-powered receipt and bank statement processing
- **Intelligent Categorization**: ML-powered expense categorization that learns from corrections
- **Predictive Budgeting**: ARIMA-based 3-month rolling budget forecasts
- **AI-Powered Recommendations**: Personalized savings advice using local or cloud LLMs
- **Emotional Engagement**: "Tamagotchi-like" agent personality that reacts to your financial health
- **Multi-Platform Access**: Web dashboard + Telegram bot for mobile convenience
- **Privacy-First Design**: Local processing by default, cloud services optional

## 🏗️ Architecture

### Technology Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 + PostgreSQL
- **Frontend**: Streamlit (interactive dashboard)
- **AI/ML**: scikit-learn, transformers, statsmodels
- **Document Processing**: Tesseract OCR, PyMuPDF, OpenCV
- **Mobile**: Telegram Bot API
- **Deployment**: Docker + Docker Compose

### Project Structure

```
personal_finance_agent/
├── app/
│   ├── api/             # FastAPI routers and endpoints
│   ├── core/            # Core logic, configuration, security
│   ├── crud/            # Database CRUD operations
│   ├── db/              # Database session management
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic validation schemas
│   ├── services/        # Business logic services
│   └── main.py          # FastAPI application entry point
├── scripts/             # Utility and maintenance scripts
├── tests/               # Pytest unit and integration tests
├── .env.example         # Environment variables template
├── Dockerfile           # Container build instructions
├── docker-compose.yml   # Multi-container orchestration
├── requirements.txt     # Python dependencies
└── streamlit_app.py     # Streamlit dashboard UI
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 13+ (or Docker)
- Tesseract OCR (for document processing)

### Installation

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd personal_finance_agent
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start with Docker (Recommended):**
   ```bash
   docker-compose up -d
   ```

6. **Or run manually:**
   ```bash
   # Start the API server
   uvicorn app.main:app --reload --port 8000
   
   # In another terminal, start the Streamlit dashboard
   streamlit run streamlit_app.py --server.port 8501
   ```

### Access the Application

- **Web Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

Key environment variables (see `.env.example` for complete list):

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT token signing key (change in production!)
- `OCR_SERVICE`: Choose between `tesseract` (local) or `google_vision` (cloud)
- `LLM_SERVICE`: Choose between `local` (transformers) or `openai` (API)

### Optional Integrations

- **OpenAI**: Set `OPENAI_API_KEY` for cloud LLM features
- **Google Calendar**: Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` for calendar integration
- **Telegram Bot**: Set `TELEGRAM_BOT_TOKEN` for mobile notifications
- **Nordigen**: Set banking API credentials for Open Banking integration

## 🧪 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff app/ tests/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🎭 Agent Personality System

The agent features an emotional state system that responds to your financial behavior:

- **Mood Score**: 0-100 scale based on savings progress and budget adherence
- **Dynamic Responses**: Advice tone changes based on current financial health
- **Achievements**: Gamification elements to maintain motivation
- **Proactive Alerts**: Notifications when intervention is needed

## 🔒 Security Features

- **JWT Authentication**: Secure API access with token-based auth
- **Password Hashing**: bcrypt for secure password storage
- **Data Encryption**: HTTPS-only communication in production
- **Privacy by Design**: Local processing prioritized over cloud services
- **Input Validation**: Pydantic schemas for data integrity

## 📊 Machine Learning Components

### Document Processing Pipeline
1. **OCR**: Extract text from receipts/statements
2. **Parsing**: Rule-based entity extraction (date, amount, vendor)
3. **Categorization**: ML classification with user feedback learning

### Budgeting Engine
1. **Time Series Analysis**: ARIMA models for expense forecasting
2. **Calendar Integration**: Incorporate planned expenses
3. **Anomaly Detection**: Identify unusual spending patterns

### Recommendation System
1. **Rule-Based**: Pattern detection for easy wins
2. **AI-Generated**: LLM-powered personalized advice
3. **Learning Loop**: Improve from user feedback

## 🚢 Deployment

### Production Deployment

1. **Environment Setup:**
   - Use strong `SECRET_KEY`
   - Set `DEBUG=False`
   - Configure production database
   - Set up HTTPS/SSL

2. **Recommended Platforms:**
   - **Fly.io**: Generous free tier, supports persistent services
   - **Railway**: Easy deployment with PostgreSQL
   - **Render**: Simple Docker deployment

3. **Docker Production:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📧 Email: support@personalfinanceagent.com
- 💬 Discord: [Community Server](https://discord.gg/example)
- 📖 Documentation: [Full Docs](https://docs.personalfinanceagent.com)

---

**⚡ Start your journey to €100,000 today!** Your AI financial companion is ready to help you achieve your savings goals with intelligent automation and personalized guidance. 