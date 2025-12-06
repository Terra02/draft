from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.view_history import (
    ViewHistoryResponse,
    ViewHistoryCreate,
    ViewHistoryUpdate,
    ViewHistoryWithContent,
)
from app.services.view_history_service import ViewHistoryService

router = APIRouter(prefix="/view-history", tags=["view-history"])

@router.get("/user/{user_id}", response_model=List[ViewHistoryWithContent])
async def get_user_view_history(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получить историю просмотров пользователя"""
    history_service = ViewHistoryService(db)
    history = await history_service.get_user_view_history_with_content(user_id, skip, limit)
    return history

@router.get("/{history_id}", response_model=ViewHistoryResponse)
async def get_view_history(history_id: int, db: AsyncSession = Depends(get_db)):
    """Получить запись истории просмотра по ID"""
    history_service = ViewHistoryService(db)
    history = await history_service.get_view_history_by_id(history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="View history record not found"
        )
    return history

@router.post("/", response_model=ViewHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_view_history(history_data: ViewHistoryCreate, db: AsyncSession = Depends(get_db)):
    """Создать запись в истории просмотров"""
    history_service = ViewHistoryService(db)
    history = await history_service.create_view_history(history_data)
    return history

@router.put("/{history_id}", response_model=ViewHistoryResponse)
async def update_view_history(
    history_id: int, 
    history_data: ViewHistoryUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Обновить запись истории просмотра"""
    history_service = ViewHistoryService(db)
    history = await history_service.update_view_history(history_id, history_data)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="View history record not found"
        )
    return history

@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_view_history(history_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить запись истории просмотра"""
    history_service = ViewHistoryService(db)
    success = await history_service.delete_view_history(history_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="View history record not found"
        )

@router.get("/user/{user_id}/stats")
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получить статистику пользователя"""
    history_service = ViewHistoryService(db)
    stats = await history_service.get_user_stats(user_id)
    return stats