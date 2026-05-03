"""Настройки приложения загрузка переменных окружения."""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        """Конфигурация загрузки переменных из файла .env."""
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
