from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, RunningWorkout
from app.schemas.running import RunningWorkoutCreate, RunningWorkoutUpdate, RunningWorkoutResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/runs", tags=["Running Workouts"])


def calculate_pace(distance_km: float, duration_seconds: int) -> int:
    """Рассчитывает темп (секунд на километр)"""
    if distance_km <= 0:
        return 0
    return int(duration_seconds / distance_km)


@router.post("/", response_model=RunningWorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_running_workout(
        workout_data: RunningWorkoutCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Добавить беговую тренировку"""

    # Рассчитываем темп
    pace = calculate_pace(workout_data.distance_km, workout_data.duration_seconds)

    # Создаём запись
    new_workout = RunningWorkout(
        user_id=current_user.id,
        distance_km=workout_data.distance_km,
        duration_seconds=workout_data.duration_seconds,
        pace_sec_per_km=pace,
        heart_rate_avg=workout_data.heart_rate_avg,
        workout_date=workout_data.workout_date,
        notes=workout_data.notes
    )

    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    return new_workout


@router.get("/", response_model=List[RunningWorkoutResponse])
def get_all_running_workouts(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100
):
    """Получить все беговые тренировки текущего пользователя"""

    workouts = db.query(RunningWorkout).filter(
        RunningWorkout.user_id == current_user.id
    ).order_by(RunningWorkout.workout_date.desc()).offset(skip).limit(limit).all()

    return workouts


@router.get("/{workout_id}", response_model=RunningWorkoutResponse)
def get_running_workout_by_id(
        workout_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получить беговую тренировку по ID"""

    workout = db.query(RunningWorkout).filter(
        RunningWorkout.id == workout_id,
        RunningWorkout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тренировка с id {workout_id} не найдена"
        )

    return workout


@router.put("/{workout_id}", response_model=RunningWorkoutResponse)
def update_running_workout(
        workout_id: int,
        workout_data: RunningWorkoutUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Обновить беговую тренировку"""

    workout = db.query(RunningWorkout).filter(
        RunningWorkout.id == workout_id,
        RunningWorkout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тренировка с id {workout_id} не найдена"
        )

    # Обновляем поля, если они переданы
    if workout_data.distance_km is not None:
        workout.distance_km = workout_data.distance_km
        # Пересчитываем темп, если изменилась дистанция или время
        new_duration = workout_data.duration_seconds or workout.duration_seconds
        workout.pace_sec_per_km = calculate_pace(workout_data.distance_km, new_duration)

    if workout_data.duration_seconds is not None:
        workout.duration_seconds = workout_data.duration_seconds
        new_distance = workout_data.distance_km or workout.distance_km
        workout.pace_sec_per_km = calculate_pace(new_distance, workout_data.duration_seconds)

    if workout_data.heart_rate_avg is not None:
        workout.heart_rate_avg = workout_data.heart_rate_avg

    if workout_data.workout_date is not None:
        workout.workout_date = workout_data.workout_date

    if workout_data.notes is not None:
        workout.notes = workout_data.notes

    db.commit()
    db.refresh(workout)

    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_running_workout(
        workout_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Удалить беговую тренировку"""

    workout = db.query(RunningWorkout).filter(
        RunningWorkout.id == workout_id,
        RunningWorkout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тренировка с id {workout_id} не найдена"
        )

    db.delete(workout)
    db.commit()

    return None  # 204 No Content