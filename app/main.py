"""
RunTrack API - приложение для бегунов
FastAPI приложение с аутентификацией, тренировками и рейтингом
"""

from fastapi import FastAPI


app = FastAPI(
    title="RunTrack API",
    description="Сервис для отслеживания тренировок бегунов, рейтинга и заданий от тренера",
    version="1.0.0",
    contact={
        "name": "Студент",
        "email": "student@example.com",
    },
)

# Корневой эндпоинт для проверки работоспособности
@app.get("/")
async def root():
    """Проверка, что сервер работает"""
    return {"message": "Welcome to RunTrack API!", "status": "running"}

# Эндпоинт для проверки здоровья сервиса
@app.get("/health")
async def health_check():
    """Проверка состояния сервера"""
    return {"status": "healthy"}