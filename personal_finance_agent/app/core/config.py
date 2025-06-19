"""
Configuration management for the Personal Finance Agent.
Loads settings from environment variables with secure defaults.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "sqlite:///./personal_finance.db"  # SQLite for testing
    test_database_url: str = "postgresql://username:password@localhost:5432/personal_finance_agent_test"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "personal_finance_agent"
    database_user: str = "username"
    database_password: str = "password"
    
    # Security and Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    app_name: str = "Personal Finance Agent"
    version: str = "2.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    allowed_hosts: List[str] = ["*"]
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Google Vision API Configuration
    google_vision_api_key: Optional[str] = None
    
    # File Upload Configuration
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Scheduler Configuration
    scheduler_timezone: str = "Europe/Helsinki"
    
    # Sentinel Guardian Configuration
    guardian_check_interval: int = 3600  # 1 hour
    risk_threshold_high: float = 0.8
    risk_threshold_medium: float = 0.5
    
    # Sentinel Learning Engine Configuration
    learning_data_retention_days: int = 365
    ml_model_update_frequency: int = 7  # days
    
    # Advanced Intelligence Configuration
    idea_engine_daily_rotation: bool = True
    income_analysis_history_days: int = 90
    liabilities_optimization_enabled: bool = True
    
    # Google Services (optional)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    # Telegram Bot (optional)
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Nordigen API (optional)
    nordigen_secret_id: Optional[str] = None
    nordigen_secret_key: Optional[str] = None
    
    # OCR Service Configuration
    ocr_service: str = "tesseract"  # Options: tesseract, google_vision
    
    # LLM Service Configuration
    llm_service: str = "local"  # Options: local, openai
    local_model_path: str = "./models/mistral-7b-instruct"
    
    # Application Settings
    log_level: str = "INFO"
    max_upload_size_mb: int = 10
    
    # File Storage
    model_directory: str = "./models"
    
    # Scheduling
    enable_scheduler: bool = True
    budget_recalc_hour: int = 6  # Hour of day to recalculate budgets
    model_retrain_days: int = 7  # How often to retrain ML models
    scheduler_max_workers: int = 4
    
    # ML Configuration
    ml_max_features: int = 10000
    ml_min_confidence_threshold: float = 0.6
    ml_min_training_samples: int = 50
    ml_retrain_threshold: int = 10  # Retrain after this many corrections
    
    # Data Retention
    document_retention_days: int = 365
    
    # Backup Configuration
    enable_backups: bool = False
    backup_dir: str = "./backups"
    log_dir: str = "./logs"
    
    # UI Configuration
    streamlit_server_port: int = 8501
    api_server_port: int = 8000
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Ensure secret key is sufficiently secure in production."""
        if not v or v == "change-this-super-secret-key-in-production":
            if not cls.debug:
                raise ValueError("SECRET_KEY must be set to a secure value in production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("ocr_service")
    def validate_ocr_service(cls, v):
        """Validate OCR service selection."""
        allowed_services = ["tesseract", "google_vision"]
        if v not in allowed_services:
            raise ValueError(f"OCR_SERVICE must be one of {allowed_services}")
        return v
    
    @validator("llm_service")
    def validate_llm_service(cls, v):
        """Validate LLM service selection."""
        allowed_services = ["local", "openai"]
        if v not in allowed_services:
            raise ValueError(f"LLM_SERVICE must be one of {allowed_services}")
        return v
    
    @validator("budget_recalc_hour")
    def validate_budget_recalc_hour(cls, v):
        """Validate budget recalculation hour."""
        if not 0 <= v <= 23:
            raise ValueError("BUDGET_RECALC_HOUR must be between 0 and 23")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_database_url(test: bool = False) -> str:
    """Get the appropriate database URL."""
    if test:
        return settings.test_database_url
    return settings.database_url


def get_upload_path() -> str:
    """Get the upload directory path, creating it if it doesn't exist."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    return settings.upload_dir


def get_model_path() -> str:
    """Get the model directory path, creating it if it doesn't exist."""
    os.makedirs(settings.model_directory, exist_ok=True)
    return settings.model_directory


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.debug


def get_data_path() -> str:
    """Get the data directory path for ML models and artifacts."""
    data_dir = os.path.join(settings.model_directory, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_logs_path() -> str:
    """Get the logs directory path, creating if necessary."""
    os.makedirs(settings.log_dir, exist_ok=True)
    return settings.log_dir


def get_backup_path() -> str:
    """Get the backup directory path, creating if necessary."""
    os.makedirs(settings.backup_dir, exist_ok=True)
    return settings.backup_dir


def is_feature_enabled(feature: str) -> bool:
    """Check if optional features are properly configured."""
    feature_checks = {
        "openai": bool(settings.openai_api_key),
        "google_calendar": bool(settings.google_client_id and settings.google_client_secret),
        "telegram": bool(settings.telegram_bot_token),
        "nordigen": bool(settings.nordigen_secret_id and settings.nordigen_secret_key),
        "google_vision": bool(settings.google_vision_api_key),
        "scheduler": settings.enable_scheduler,
    }
    return feature_checks.get(feature, False) 