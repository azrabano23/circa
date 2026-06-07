from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Circa"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://circa_user:circa_password@localhost:5432/circa_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Google APIs
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Canvas LMS
    CANVAS_API_URL: str = "https://canvas.instructure.com/api/v1"
    CANVAS_API_KEY: str = ""
    
    # Notion
    NOTION_API_KEY: str = ""
    NOTION_VERSION: str = "2022-06-28"
    
    # Health APIs
    APPLE_HEALTH_KEY: str = ""
    GOOGLE_FIT_CLIENT_ID: str = ""
    GOOGLE_FIT_CLIENT_SECRET: str = ""
    
    # Gmail
    GMAIL_SCOPES: str = "https://www.googleapis.com/auth/gmail.readonly"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

