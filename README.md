# RunTrack API

Сервис для отслеживания тренировок бегунов, рейтинга и достижений.

## Автор

Ваше Имя

## Описание проекта

RunTrack API — это REST-сервис на FastAPI, который позволяет:
- Регистрировать пользователей и аутентифицироваться по JWT
- Добавлять беговые тренировки (дистанция, время, пульс)
- Просматривать рейтинг бегунов по километражу за день/неделю/месяц
- Получать достижения (геймификация)

## Технологии

- FastAPI
- SQLAlchemy
- SQLite
- JWT аутентификация
- Pytest

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/victoriag4/runtrack-api.git
cd runtrack-api
 
### 2. Создание виртуального окружения


python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # macOS/Linux

3. Установка зависимостей

pip install -r requirements.txt

4. Настройка переменных окружения

DATABASE_URL=sqlite:///./runtrack.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

5. Запуск сервера

fastapi dev app/main.py

6. Документация

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc


