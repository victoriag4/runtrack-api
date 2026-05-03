import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_user_and_add_workouts(username_prefix, distance, workout_date="2025-04-28"):
    """Вспомогательная функция: создаёт пользователя и добавляет тренировки"""
    import time
    unique_suffix = int(time.time())

    # Регистрация
    register_response = client.post("/auth/register", json={
        "username": f"{username_prefix}_{unique_suffix}",
        "email": f"{username_prefix}_{unique_suffix}@example.com",
        "password": "123456",
        "role": "runner"
    })
    user_id = register_response.json()["id"]

    # Логин
    login_response = client.post("/auth/login", json={
        "email": f"{username_prefix}_{unique_suffix}@example.com",
        "password": "123456"
    })
    token = login_response.json()["access_token"]

    # Добавляем тренировки
    workout_data = {
        "distance_km": distance,
        "duration_seconds": distance * 300,  # темп 5 мин/км
        "workout_date": workout_date
    }
    client.post("/runs/", json=workout_data, headers={"Authorization": f"Bearer {token}"})

    return {"user_id": user_id, "token": token, "distance": distance}


class TestRating:
    """Тесты для рейтинга и статистики"""

    def test_get_rating_week(self):
        """Тест получения рейтинга за неделю"""
        # Создаём пользователя и получаем токен
        user = create_user_and_add_workouts("runner_a", 10.0)

        # Рейтинг доступен только авторизованным пользователям
        response = client.get(
            "/rating/?period=week&limit=10",
            headers={"Authorization": f"Bearer {user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "week"
        assert "top_runners" in data
        assert isinstance(data["top_runners"], list)

    def test_get_rating_with_auth(self):
        """Тест рейтинга с авторизацией (должен показать место пользователя)"""
        # Создаём пользователя
        user = create_user_and_add_workouts("auth_user", 15.0)

        response = client.get(
            "/rating/?period=all",
            headers={"Authorization": f"Bearer {user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_rank" in data
        if data["user_rank"]:
            assert data["user_rank"]["total_km"] >= 15.0

    def test_get_achievements(self):
        """Тест получения достижений пользователя"""
        user = create_user_and_add_workouts("achievement_user", 5.0)

        response = client.get(
            "/rating/achievements",
            headers={"Authorization": f"Bearer {user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "achievements" in data
        assert isinstance(data["achievements"], list)
        # Первая тренировка должна дать достижение "Первый шаг"
        assert any("Первый" in a["name"] for a in data["achievements"])

    def test_get_my_stats(self):
        """Тест получения статистики пользователя"""
        user = create_user_and_add_workouts("stats_user", 8.0)

        response = client.get(
            "/rating/stats/me",
            headers={"Authorization": f"Bearer {user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_km"] >= 8.0
        assert data["total_workouts"] >= 1
        assert "best_pace" in data

    def test_rating_with_different_periods(self):
        """Тест рейтинга с разными периодами"""
        # Создаём пользователя для авторизации
        user = create_user_and_add_workouts("rating_user", 5.0)
        headers = {"Authorization": f"Bearer {user['token']}"}

        response_day = client.get("/rating/?period=day", headers=headers)
        response_week = client.get("/rating/?period=week", headers=headers)
        response_month = client.get("/rating/?period=month", headers=headers)
        response_all = client.get("/rating/?period=all", headers=headers)

        assert response_day.status_code == 200
        assert response_week.status_code == 200
        assert response_month.status_code == 200
        assert response_all.status_code == 200
