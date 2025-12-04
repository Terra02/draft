from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

# Простая зависимость для получения сессии БД
get_db_session = get_db