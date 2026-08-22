from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_user_can_register_and_login():
    registration = client.post(
        "/api/auth/register",
        json={"name": "Maya Patel", "email": "maya@example.com", "password": "SecurePass123!"},
    )
    assert registration.status_code == 201
    assert registration.json()["user"]["role"] == "user"

    login = client.post(
        "/api/auth/login",
        json={"email": "maya@example.com", "password": "SecurePass123!"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_login_rejects_invalid_password():
    response = client.post(
        "/api/auth/login", json={"email": "missing@example.com", "password": "incorrect"}
    )
    assert response.status_code == 401
