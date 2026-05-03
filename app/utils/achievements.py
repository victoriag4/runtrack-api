"""Утилиты для расчёта достижений и статистики пользователей."""

from sqlalchemy.orm import Session

from app.models import RunningWorkout
from typing import Dict, Any, List


# Список всех возможных достижений
ACHIEVEMENTS = {
    "first_workout": {
        "name": " Первый шаг",
        "description": "Добавлена первая тренировка",
        "icon": "",
        "condition": lambda stats: stats["total_workouts"] >= 1
    },
    "ten_km": {
        "name": " 10 км",
        "description": "Суммарный километраж превысил 10 км",
        "icon": "",
        "condition": lambda stats: stats["total_km"] >= 10
    },
    "fifty_km": {
        "name": " 50 км",
        "description": "Суммарный километраж превысил 50 км",
        "icon": "⭐",
        "condition": lambda stats: stats["total_km"] >= 50
    },
    "hundred_km": {
        "name": " 100 км",
        "description": "Суммарный километраж превысил 100 км! Вы настоящий бегун!",
        "icon": "",
        "condition": lambda stats: stats["total_km"] >= 100
    },
    "marathon": {
        "name": " Марафонец",
        "description": "Одна тренировка длиннее 42 км",
        "icon": "",
        "condition": lambda stats: stats["max_distance"] >= 42.2
    },
    "sprinter": {
        "name": "⚡ Спринтер",
        "description": "Темп быстрее 4 мин/км (240 сек/км)",
        "icon": "⚡",
        "condition": lambda stats: stats["best_pace"] is not None and stats["best_pace"] < 240
    },
    "early_bird": {
        "name": " Ранняя пташка",
        "description": "Тренировка до 7 утра",
        "icon": "",
        "condition": lambda stats: stats["has_early_workout"]
    },
    "consistent": {
        "name": " Упорный",
        "description": "Тренировки 5 дней подряд",
        "icon": "",
        "condition": lambda stats: stats["max_streak"] >= 5
    },
    "speedster": {
        "name": " Скорость",
        "description": "Лучший темп быстрее 5 мин/км (300 сек/км)",
        "icon": "",
        "condition": lambda stats: stats["best_pace"] is not None and stats["best_pace"] < 300
    },
    "dedicated": {
        "name": " Преданный",
        "description": "Более 20 тренировок",
        "icon": " ",
        "condition": lambda stats: stats["total_workouts"] >= 20
    }
}


def calculate_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Рассчитывает статистику пользователя для достижений."""
    workouts = db.query(RunningWorkout).filter(
        RunningWorkout.user_id == user_id
    ).all()

    if not workouts:
        return {
            "total_km": 0,
            "total_workouts": 0,
            "max_distance": 0,
            "best_pace": None,
            "has_early_workout": False,
            "max_streak": 0
        }

    total_km = sum(w.distance_km for w in workouts)
    total_workouts = len(workouts)
    max_distance = max(w.distance_km for w in workouts)

    # Лучший темп (минимальное значение)
    paces = [w.pace_sec_per_km for w in workouts if w.pace_sec_per_km]
    best_pace = min(paces) if paces else None

    # Проверка на ранние тренировки (до 7 утра)
    # В SQLite нет прямого доступа к времени, для простоты пропустим
    has_early_workout = False

    # Расчёт максимальной серии дней подряд
    dates = sorted(set(w.workout_date for w in workouts))
    max_streak = 1
    current_streak = 1

    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return {
        "total_km": total_km,
        "total_workouts": total_workouts,
        "max_distance": max_distance,
        "best_pace": best_pace,
        "has_early_workout": has_early_workout,
        "max_streak": max_streak
    }


def get_user_achievements(db: Session, user_id: int) -> List[Dict[str, str]]:
    """Возвращает список достижений пользователя."""
    stats = calculate_user_stats(db, user_id)

    achievements = []
    for achievement in ACHIEVEMENTS.values():
        if achievement["condition"](stats):
            achievements.append({
                "name": achievement["name"],
                "description": achievement["description"],
                "icon": achievement["icon"]
            })

    return achievements