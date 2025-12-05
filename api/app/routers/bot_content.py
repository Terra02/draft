# api/app/api/endpoints/bot_content.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services.content_service import ContentService

router = APIRouter()

@router.get("/bot/search")
async def bot_search_content(
    title: str,
    content_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Поиск контента для бота (сначала в БД, потом в OMDB через Worker)"""
    content_service = ContentService(db)
    
    result = await content_service.search_omdb_direct(title, content_type)
    
    if result["source"] == "not_found":
        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )
    
    return result

@router.post("/bot/add-from-omdb")
async def bot_add_from_omdb(
    title: str,
    content_type: str = "movie",
    db: AsyncSession = Depends(get_db)
):
    """Добавить фильм из OMDB для бота"""
    content_service = ContentService(db)
    
    result = await content_service.add_from_omdb(title, content_type)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Не удалось добавить фильм")
        )
    
    return result