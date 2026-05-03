"""Модели базы данных SQLAlchemy для приложения RunTrack."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Модель пользователя (бегун или тренер)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="runner")  # admin, trainer, runner
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    running_workouts = relationship(
        "RunningWorkout", back_populates="user", cascade="all, delete-orphan"
    )
    gpp_workouts = relationship(
        "GPPWorkout", back_populates="user", cascade="all, delete-orphan"
    )
    assignments_received = relationship(
        "Assignment", foreign_keys="Assignment.runner_id", back_populates="runner"
    )
    assignments_given = relationship(
        "Assignment", foreign_keys="Assignment.trainer_id", back_populates="trainer"
    )


class RunningWorkout(Base):
    """Модель беговой тренировки."""

    __tablename__ = "running_workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    distance_km = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    pace_sec_per_km = Column(Integer, nullable=True)
    heart_rate_avg = Column(Integer, nullable=True)
    workout_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь
    user = relationship("User", back_populates="running_workouts")


class GPPWorkout(Base):
    """Модель тренировки ОФП (общефизическая подготовка)."""

    __tablename__ = "gpp_workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String(100), nullable=False)
    sets_count = Column(Integer, nullable=True)
    reps_count = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    workout_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь
    user = relationship("User", back_populates="gpp_workouts")


class Assignment(Base):
    """Модель задания от тренера бегуну."""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    runner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_type = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    target_value = Column(String(100), nullable=True)
    completed = Column(Boolean, default=False)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    trainer = relationship(
        "User", foreign_keys=[trainer_id], back_populates="assignments_given"
    )
    runner = relationship(
        "User", foreign_keys=[runner_id], back_populates="assignments_received"
    )