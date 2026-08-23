from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import User


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


def test_admin_can_manage_users_but_not_remove_own_access():
    client.post("/api/auth/register", json={"name": "Admin User", "email": "admin@example.com", "password": "SecurePass123!"})
    client.post("/api/auth/register", json={"name": "Customer", "email": "customer@example.com", "password": "SecurePass123!"})
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "admin@example.com").one()
    customer = db.query(User).filter(User.email == "customer@example.com").one()
    admin.role = "admin"
    db.commit()
    admin_id, customer_id = admin.id, customer.id
    db.close()
    token = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "SecurePass123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert len(client.get("/api/admin/users", headers=headers).json()) == 2
    updated = client.put(f"/api/admin/users/{customer_id}", headers=headers, json={"role": "admin", "email_verified": True})
    assert updated.status_code == 200
    assert updated.json()["role"] == "admin"
    assert updated.json()["email_verified"] is True
    assert client.put(f"/api/admin/users/{admin_id}", headers=headers, json={"role": "user"}).status_code == 400
    assert client.delete(f"/api/admin/users/{customer_id}", headers=headers).status_code == 204
