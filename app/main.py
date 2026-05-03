from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, runs, rating

# Создаём таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RunTrack API",
    description="Сервис для отслеживания тренировок бегунов",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(runs.router)
app.include_router(rating.router)


@app.get("/")
def root():
    return {"message": "Welcome to RunTrack API!", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}