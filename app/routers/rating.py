"""Рейтинг бегунов, достижения и статистика."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, RunningWorkout
from app.schemas.rating import (
    RatingResponse, RunnerStats, UserRankInfo,
    UserAchievementsResponse, Achievement
)
from app.utils.auth import get_current_user
from app.utils.achievements import get_user_achievements, calculate_user_stats

router = APIRouter(prefix="/rating", tags=["Rating & Achievements"])


def _get_date_filter(period: str, target_date: date = None):
    """Возвращает фильтр по дате для заданного периода."""
    if target_date is None:
        target_date = date.today()

    if period == "day":
        return target_date
    if period == "week":
        return target_date - timedelta(days=7)
    if period == "month":
        return target_date - timedelta(days=30)
    return None  # period == "all"


def _get_user_rank_and_km(db: Session, user_id: int, date_filter, period: str):
    """Возвращает место пользователя в рейтинге и его километраж."""
    query = db.query(
        RunningWorkout.user_id,
        func.sum(RunningWorkout.distance_km).label("total_km")
    )
    if date_filter:
        if period == "day":
            query = query.filter(RunningWorkout.workout_date == date_filter)
        else:
            query = query.filter(RunningWorkout.workout_date >= date_filter)

    results = query.group_by(RunningWorkout.user_id).all()
    sorted_results = sorted(results, key=lambda x: x[1] or 0, reverse=True)

    for rank, (uid, total_km) in enumerate(sorted_results, start=1):
        if uid == user_id:
            return rank, float(total_km or 0)
    return None, 0


@router.get("/", response_model=RatingResponse)
def get_rating(
    period: str = Query("week", description="Период: day, week, month, all"),
    limit: int = Query(10, ge=1, le=50, description="Количество бегунов в топе"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Рейтинг бегунов по суммарному километражу за период.
    Бизнес-задача: расчёт рейтинга с алгоритмическим компонентом.
    """
    # Фильтр по дате
    date_filter = _get_date_filter(period)

    # Базовый запрос: сумма километров по пользователям
    query = db.query(
        RunningWorkout.user_id,
        func.sum(RunningWorkout.distance_km).label("total_km"),
        func.count(RunningWorkout.id).label("workouts_count"),
        func.max(RunningWorkout.distance_km).label("best_distance"),
        func.avg(RunningWorkout.pace_sec_per_km).label("avg_pace")
    )

    # Применяем фильтр по дате
    if date_filter:
        if period == "day":
            query = query.filter(RunningWorkout.workout_date == date_filter)
        else:
            query = query.filter(RunningWorkout.workout_date >= date_filter)

    # Группировка и сортировка
    results = query.group_by(RunningWorkout.user_id).order_by(
        func.sum(RunningWorkout.distance_km).desc()
    ).limit(limit).all()

    # Получаем имена пользователей
    user_ids = [r[0] for r in results]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u for u in users}

    # Формируем топ бегунов
    top_runners = []
    for rank, result in enumerate(results, start=1):
        uid, total_km, wc, best_dist, avg_pace = result
        user = user_map.get(uid)
        if user:
            top_runners.append(RunnerStats(
                rank=rank,
                user_id=uid,
                username=user.username,
                total_km=float(total_km or 0),
                avg_pace=int(avg_pace) if avg_pace else None,
                workouts_count=wc,
                best_distance=float(best_dist or 0)
            ))

    # Находим место текущего пользователя
    user_rank, user_total_km = _get_user_rank_and_km(db, current_user.id, date_filter, period)

    user_rank_info = None
    if user_rank:
        need_to_next = None
        if user_rank > 1:
            # Получаем километраж предыдущего места
            prev_km_query = db.query(
                func.sum(RunningWorkout.distance_km).label("total_km")
            )
            if date_filter:
                if period == "day":
                    prev_km_query = prev_km_query.filter(
                        RunningWorkout.workout_date == date_filter
                    )
                else:
                    prev_km_query = prev_km_query.filter(
                        RunningWorkout.workout_date >= date_filter
                    )
            prev_results = prev_km_query.group_by(
                RunningWorkout.user_id
            ).order_by(
                func.sum(RunningWorkout.distance_km).desc()
            ).limit(user_rank).all()

            if len(prev_results) >= user_rank:
                prev_km = prev_results[user_rank - 1][0] or 0
                need_to_next = float(prev_km - user_total_km)

        user_rank_info = UserRankInfo(
            rank=user_rank,
            total_km=user_total_km,
            need_to_next=round(need_to_next, 2) if need_to_next and need_to_next > 0 else None
        )

    return RatingResponse(
        period=period,
        top_runners=top_runners,
        user_rank=user_rank_info
    )


@router.get("/achievements", response_model=UserAchievementsResponse)
def get_my_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить достижения текущего пользователя (геймификация)."""
    achievements = get_user_achievements(db, current_user.id)

    achievement_objects = [
        Achievement(
            name=a["name"],
            description=a["description"],
            icon=a["icon"]
        )
        for a in achievements
    ]

    return UserAchievementsResponse(
        user_id=current_user.id,
        username=current_user.username,
        achievements=achievement_objects
    )


@router.get("/stats/me")
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить подробную статистику текущего пользователя."""
    stats = calculate_user_stats(db, current_user.id)

    best_pace_min = None
    if stats["best_pace"]:
        minutes = stats["best_pace"] // 60
        seconds = stats["best_pace"] % 60
        best_pace_min = f"{minutes}:{seconds:02d}"

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_km": round(stats["total_km"], 2),
        "total_workouts": stats["total_workouts"],
        "max_distance": round(stats["max_distance"], 2) if stats["max_distance"] else 0,
        "best_pace": stats["best_pace"],
        "best_pace_min_per_km": best_pace_min,
        "max_streak": stats["max_streak"]
    }