from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password123@postgres:5432/movie_tracker"
    
    # JWT
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # API
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # External APIs
    omdb_api_key: Optional[str] = None
    
    # Search settings
    search_external_timeout: int = 10
    max_external_results: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Глобальный экземпляр настроек
settings = Settings()