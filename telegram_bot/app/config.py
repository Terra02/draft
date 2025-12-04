from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str

    # API
    API_URL: str = "http://api:8000"
    
    API_PREFIX: str = "/api/v1"  

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    class Config:
        env_file = ".env"

settings = Settings()