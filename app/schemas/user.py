"""Pydantic схемы для пользователей и аутентификации."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Схема для регистрации нового пользователя."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    role: str = Field(default="runner")


class UserLogin(BaseModel):
    """Схема для входа пользователя."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        """Конфигурация Pydantic для работы с SQLAlchemy моделями."""
        from_attributes = True


class Token(BaseModel):
    """Схема ответа с JWT токеном."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Схема данных из JWT токена."""
    email: Optional[str] = None