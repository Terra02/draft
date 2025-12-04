from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio

from app.routers import (
    users_router, content_router, view_history_router,
    watchlist_router, analytics_router, categories_router
)

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

app.include_router(users_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(view_history_router, prefix="/api/v1")
app.include_router(watchlist_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Movie Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}