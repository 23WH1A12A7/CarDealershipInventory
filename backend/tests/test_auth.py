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


def test_duplicate_email_is_rejected():
    payload = {"name": "Maya Patel", "email": "maya@example.com", "password": "SecurePass123!"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_public_registration_cannot_create_administrator():
    response = client.post(
        "/api/auth/register",
        json={"name": "Mal Admin", "email": "mal@example.com", "password": "SecurePass123!", "role": "admin"},
    )
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "user"
