from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: Optional[str] = Field(None, max_length=50, description="Имя пользователя в Telegram")
    first_name: Optional[str] = Field(None, max_length=100, description="Имя пользователя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия пользователя")
    email: Optional[EmailStr] = Field(None, description="Email пользователя")

class UserCreate(UserBase):
    """Схема для создания пользователя"""
    pass

class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    username: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    """Схема ответа для пользователя"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True