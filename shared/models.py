"""
Общие модели Pydantic для всех сервисов
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Generic, TypeVar, List
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel):
    """Базовая модель ответа"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Модель пагинированного ответа"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class HealthCheckResponse(BaseModel):
    """Модель ответа для проверки здоровья"""
    status: str
    service: str
    timestamp: datetime
    version: str = "1.0.0"