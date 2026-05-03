from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class RunningWorkoutCreate(BaseModel):
    """Схема для создания тренировки"""
    distance_km: float = Field(..., gt=0, le=100, description="Дистанция в км")
    duration_seconds: int = Field(..., gt=0, description="Длительность в секундах")
    heart_rate_avg: Optional[int] = Field(None, ge=30, le=250, description="Средний пульс")
    workout_date: date = Field(..., description="Дата тренировки")
    notes: Optional[str] = Field(None, max_length=500, description="Заметки")

class RunningWorkoutUpdate(BaseModel):
    """Схема для обновления тренировки (все поля необязательные)"""
    distance_km: Optional[float] = Field(None, gt=0, le=100)
    duration_seconds: Optional[int] = Field(None, gt=0)
    heart_rate_avg: Optional[int] = Field(None, ge=30, le=250)
    workout_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

class RunningWorkoutResponse(BaseModel):
    """Схема для ответа с тренировкой"""
    id: int
    user_id: int
    distance_km: float
    duration_seconds: int
    pace_sec_per_km: Optional[int] = None  # темп (секунд на км)
    heart_rate_avg: Optional[int] = None
    workout_date: date
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True