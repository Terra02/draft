# api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio


from app.routers import (
    users_router, content_router, view_history_router,
    watchlist_router, analytics_router, categories_router
)

# Импортируем роутер для бота
from app.routers.bot_content import router as bot_content_router
##для теста
from app.emergency_bot import emergency_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movie Tracker API",
    description="API для отслеживания фильмов и сериалов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(users_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(view_history_router, prefix="/api/v1")
app.include_router(watchlist_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
#для теста
app.include_router(emergency_router, prefix="/api/v1/emergency/bot")

# Подключаем роутер для бота
app.include_router(bot_content_router, prefix="/api/v1", tags=["bot"])



@app.get("/")
async def root():
    return {"message": "Movie Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Добавляем обработку graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединений при выключении"""
    from app.services.worker_adapter import worker_adapter
    await worker_adapter.close()
    logger.info("Worker adapter closed")