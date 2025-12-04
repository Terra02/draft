from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import logging

# Импортируем настройки
try:
    from app.config import settings
except ImportError:
    # Запасной вариант если config еще не настроен
    class Settings:
        database_url = "postgresql+asyncpg://postgres:password123@postgres:5432/movie_tracker"
        debug = True
    settings = Settings()

logger = logging.getLogger(__name__)

# Создание асинхронного движка
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_size=20,
    max_overflow=30
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# ------------------------------------------------------------------
# ВАЖНО: Импорт всех моделей ДОЛЖЕН быть ЗДЕСЬ, после объявления Base
# ------------------------------------------------------------------

from app.models.user import User
from app.models.category import Category
from app.models.content import Content
from app.models.view_history import ViewHistory
from app.models.watchlist import Watchlist

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

