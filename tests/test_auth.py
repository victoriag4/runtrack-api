import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)


def get_unique_user():
    """Генерирует уникальные тестовые данные"""
    unique_suffix = int(time.time() * 1000)
    return {
        "username": f"testuser_{unique_suffix}",
        "email": f"test_{unique_suffix}@example.com",
        "password": "123456",
        "role": "runner"
    }


class TestAuth:
    """Тесты для аутентификации и регистрации"""

    def test_register_success(self):
        """Тест успешной регистрации"""
        test_user = get_unique_user()
        response = client.post("/auth/register", json=test_user)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]
        assert "id" in data
        assert "created_at" in data

    def test_register_duplicate_email(self):
        """Тест регистрации с уже существующим email"""
        test_user = get_unique_user()
        # Первая регистрация
        client.post("/auth/register", json=test_user)
        # Вторая регистрация с тем же email
        response = client.post("/auth/register", json=test_user)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_register_duplicate_username(self):
        """Тест регистрации с уже существующим username"""
        test_user = get_unique_user()
        # Первая регистрация
        client.post("/auth/register", json=test_user)
        # Вторая регистрация с тем же username, но другим email
        duplicate_username_user = {
            "username": test_user["username"],
            "email": f"unique_{int(time.time())}@example.com",
            "password": "123456",
            "role": "runner"
        }
        response = client.post("/auth/register", json=duplicate_username_user)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_register_invalid_email(self):
        """Тест регистрации с неверным email"""
        invalid_user = {
            "username": "invalid",
            "email": "not-an-email",
            "password": "123456",
            "role": "runner"
        }
        response = client.post("/auth/register", json=invalid_user)
        assert response.status_code == 422

    def test_register_short_password(self):
        """Тест регистрации с коротким паролем (<6 символов)"""
        short_password_user = {
            "username": "shortpass",
            "email": "short@example.com",
            "password": "123",
            "role": "runner"
        }
        response = client.post("/auth/register", json=short_password_user)
        assert response.status_code == 422

    def test_login_success(self):
        """Тест успешного входа"""
        test_user = get_unique_user()
        client.post("/auth/register", json=test_user)

        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """Тест входа с неверным паролем"""
        test_user = get_unique_user()
        client.post("/auth/register", json=test_user)

        login_data = {
            "email": test_user["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]

    def test_login_user_not_found(self):
        """Тест входа с несуществующим email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "123456"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_current_user(self):
        """Тест получения информации о текущем пользователе с токеном"""
        test_user = get_unique_user()
        client.post("/auth/register", json=test_user)

        # Получаем токен
        login_response = client.post("/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        token = login_response.json()["access_token"]

        # Запрашиваем информацию о пользователе
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]

    def test_get_current_user_without_token(self):
        """Тест доступа без токена (должен вернуть 401)"""
        response = client.get("/auth/me")
        assert response.status_code == 401