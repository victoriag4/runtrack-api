"""Подключение к базе данных SQLite и управление сессиями."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Для SQLite нужно добавить check_same_thread=False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=True,  # Выводит SQL-запросы в консоль (полезно для отладки)
)
# Фабрика сессий (константа, поэтому UPPER_CASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей

Base = declarative_base()

def get_db():
    """
        Генератор сессии базы данных для Dependency Injection.

        Yields:
            Session: Сессия SQLAlchemy для работы с БД.
        """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()