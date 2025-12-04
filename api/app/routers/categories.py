from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Получить все категории"""
    category_service = CategoryService(db)
    categories = await category_service.get_categories_with_stats()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Получить категорию по ID"""
    category_service = CategoryService(db)
    category = await category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """Создать новую категорию"""
    category_service = CategoryService(db)
    category = await category_service.create_category(category_data)
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int, 
    category_data: CategoryUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Обновить категорию"""
    category_service = CategoryService(db)
    category = await category_service.update_category(category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить категорию"""
    category_service = CategoryService(db)
    success = await category_service.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )