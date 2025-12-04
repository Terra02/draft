from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password123@localhost:5432/movie_tracker"
    
    # API
    API_URL: str = "http://api:8000"
    
    # OMDb API
    OMDB_API_KEY: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Worker settings
    WORKER_ENABLED: bool = True
    CLEANUP_ENABLED: bool = True
    NOTIFICATIONS_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings():
    return Settings()