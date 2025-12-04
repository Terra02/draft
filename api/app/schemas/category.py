from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    """Базовая схема категории"""
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(None, max_length=500, description="Описание категории")

class CategoryCreate(CategoryBase):
    """Схема для создания категории"""
    pass

class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(None, max_length=500, description="Описание категории")

class CategoryResponse(CategoryBase):
    """Схема ответа для категории"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True