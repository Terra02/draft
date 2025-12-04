from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.user import UserResponse, UserCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(100, ge=1, le=100, description="Лимит записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список пользователей"""
    service = UserService(db)
    users = await service.get_users(skip=skip, limit=limit)
    return users

@router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить пользователя по Telegram ID"""
    service = UserService(db)
    user = await service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать нового пользователя"""
    service = UserService(db)
    
    # Проверяем, существует ли пользователь с таким Telegram ID
    existing_user = await service.get_user_by_telegram_id(user_data.telegram_id)
    if existing_user:
        return existing_user
    
    user = await service.create_user(user_data)
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить пользователя по ID"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user