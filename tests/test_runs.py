import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_test_user_and_get_token():
    """Вспомогательная функция: создаёт пользователя и возвращает токен"""
    # Уникальный email для каждого теста
    import time
    unique_email = f"test_{int(time.time())}@example.com"

    register_response = client.post("/auth/register", json={
        "username": f"runner_{int(time.time())}",
        "email": unique_email,
        "password": "123456",
        "role": "runner"
    })

    login_response = client.post("/auth/login", json={
        "email": unique_email,
        "password": "123456"
    })

    return login_response.json()["access_token"]


class TestRuns:
    """Тесты для беговых тренировок"""

    def test_create_workout_success(self):
        """Тест успешного создания тренировки"""
        token = create_test_user_and_get_token()

        workout_data = {
            "distance_km": 5.0,
            "duration_seconds": 1500,
            "heart_rate_avg": 145,
            "workout_date": "2025-04-28",
            "notes": "Утренняя пробежка"
        }

        response = client.post(
            "/runs/",
            json=workout_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["distance_km"] == 5.0
        assert data["duration_seconds"] == 1500
        assert data["user_id"] is not None
        # Проверяем, что темп рассчитался правильно
        assert data["pace_sec_per_km"] == 300  # 1500 / 5 = 300

    def test_create_workout_without_auth(self):
        """Тест создания тренировки без авторизации"""
        workout_data = {
            "distance_km": 5.0,
            "duration_seconds": 1500,
            "heart_rate_avg": 145,
            "workout_date": "2025-04-28"
        }

        response = client.post("/runs/", json=workout_data)
        assert response.status_code == 401

    def test_create_workout_invalid_data(self):
        """Тест создания тренировки с неверными данными"""
        token = create_test_user_and_get_token()

        # Отрицательная дистанция
        workout_data = {
            "distance_km": -5.0,
            "duration_seconds": 1500,
            "workout_date": "2025-04-28"
        }

        response = client.post(
            "/runs/",
            json=workout_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422

    def test_get_all_workouts(self):
        """Тест получения всех тренировок пользователя"""
        token = create_test_user_and_get_token()

        # Добавляем тренировку
        workout_data = {
            "distance_km": 10.0,
            "duration_seconds": 3000,
            "heart_rate_avg": 150,
            "workout_date": "2025-04-28"
        }
        client.post("/runs/", json=workout_data, headers={"Authorization": f"Bearer {token}"})

        # Получаем список тренировок
        response = client.get("/runs/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_workout_by_id(self):
        """Тест получения конкретной тренировки по ID"""
        token = create_test_user_and_get_token()

        # Создаём тренировку
        workout_data = {
            "distance_km": 8.0,
            "duration_seconds": 2400,
            "heart_rate_avg": 148,
            "workout_date": "2025-04-28"
        }
        create_response = client.post(
            "/runs/",
            json=workout_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        workout_id = create_response.json()["id"]

        # Получаем тренировку по ID
        response = client.get(
            f"/runs/{workout_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workout_id
        assert data["distance_km"] == 8.0

    def test_get_workout_not_found(self):
        """Тест получения несуществующей тренировки"""
        token = create_test_user_and_get_token()

        response = client.get(
            "/runs/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]

    def test_update_workout(self):
        """Тест обновления тренировки"""
        token = create_test_user_and_get_token()

        # Создаём тренировку
        workout_data = {
            "distance_km": 5.0,
            "duration_seconds": 1500,
            "workout_date": "2025-04-28"
        }
        create_response = client.post(
            "/runs/",
            json=workout_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        workout_id = create_response.json()["id"]

        # Обновляем тренировку
        update_data = {
            "distance_km": 6.0,
            "duration_seconds": 1800,
            "notes": "Обновлённая тренировка"
        }
        response = client.put(
            f"/runs/{workout_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["distance_km"] == 6.0
        assert data["duration_seconds"] == 1800
        assert data["notes"] == "Обновлённая тренировка"

    def test_delete_workout(self):
        """Тест удаления тренировки"""
        token = create_test_user_and_get_token()

        # Создаём тренировку
        workout_data = {
            "distance_km": 3.0,
            "duration_seconds": 900,
            "workout_date": "2025-04-28"
        }
        create_response = client.post(
            "/runs/",
            json=workout_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        workout_id = create_response.json()["id"]

        # Удаляем тренировку
        response = client.delete(
            f"/runs/{workout_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

        # Проверяем, что тренировка удалена
        get_response = client.get(
            f"/runs/{workout_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404