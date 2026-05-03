from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class RunnerStats(BaseModel):
    """Статистика одного бегуна в рейтинге"""
    rank: int
    user_id: int
    username: str
    total_km: float
    avg_pace: Optional[int] = None  # средний темп (сек/км)
    workouts_count: int
    best_distance: float

class UserRankInfo(BaseModel):
    """Информация о месте текущего пользователя"""
    rank: int
    total_km: float
    need_to_next: Optional[float] = None  # сколько км не хватает до следующего места

class RatingResponse(BaseModel):
    """Ответ с рейтингом"""
    period: str  # week, month, all
    top_runners: List[RunnerStats]
    user_rank: Optional[UserRankInfo] = None

class Achievement(BaseModel):
    """Достижение бегуна"""
    name: str
    description: str
    icon: str

class UserAchievementsResponse(BaseModel):
    """Ответ с достижениями пользователя"""
    user_id: int
    username: str
    achievements: List[Achievement]