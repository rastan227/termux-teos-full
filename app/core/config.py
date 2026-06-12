import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # General
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./teos.db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "40"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_WEBHOOK_URL: str = os.getenv("BOT_WEBHOOK_URL", "")
    BOT_WEBHOOK_PATH: str = os.getenv("BOT_WEBHOOK_PATH", "/webhook")
    USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "false").lower() == "true"
    POLLING_TIMEOUT: int = int(os.getenv("POLLING_TIMEOUT", "30"))
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_CORS_ORIGINS: List[str] = ["*"]
    
    # Security
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    RATE_LIMIT_PER_USER: str = os.getenv("RATE_LIMIT_PER_USER", "100/minute")
    ADMIN_IDS: List[int] = []
    
    # AI
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.7"))
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "true").lower() == "true"
    
    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")
    STORAGE_LOCAL_PATH: str = os.getenv("STORAGE_LOCAL_PATH", "./storage")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    
    # Payment
    PAYMENT_MOCK: bool = os.getenv("PAYMENT_MOCK", "true").lower() == "true"
    PAYMENT_CALLBACK_URL: str = os.getenv("PAYMENT_CALLBACK_URL", "")
    
    # Monitoring
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    
    # Auto Update
    AUTO_UPDATE_ENABLED: bool = os.getenv("AUTO_UPDATE_ENABLED", "false").lower() == "true"
    UPDATE_CHECK_INTERVAL_HOURS: int = int(os.getenv("UPDATE_CHECK_INTERVAL_HOURS", "24"))
    GIT_REPO_URL: str = os.getenv("GIT_REPO_URL", "")
    
    # Backup
    BACKUP_CRON_SCHEDULE: str = os.getenv("BACKUP_CRON_SCHEDULE", "0 2 * * *")
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
    
    # Feature Flags
    FEATURE_MUSIC_ENABLED: bool = os.getenv("FEATURE_MUSIC_ENABLED", "true").lower() == "true"
    FEATURE_VPN_ENABLED: bool = os.getenv("FEATURE_VPN_ENABLED", "true").lower() == "true"
    FEATURE_WALLET_ENABLED: bool = os.getenv("FEATURE_WALLET_ENABLED", "true").lower() == "true"
    FEATURE_TICKET_ENABLED: bool = os.getenv("FEATURE_TICKET_ENABLED", "true").lower() == "true"
    FEATURE_PLUGINS_ENABLED: bool = os.getenv("FEATURE_PLUGINS_ENABLED", "true").lower() == "true"

settings = Settings()
