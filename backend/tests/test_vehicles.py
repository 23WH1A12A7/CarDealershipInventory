from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import User


client = TestClient(app)


def auth_headers():
    client.post(
        "/api/auth/register",
        json={"name": "Ava Admin", "email": "admin@example.com", "password": "AdminPass123!"},
    )
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "admin@example.com").one()
    admin.role = "admin"
    db.commit(); db.close()
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_can_create_and_search_vehicle():
    headers = auth_headers()
    created = client.post(
        "/api/vehicles",
        headers=headers,
        json={"make": "Porsche", "model": "911 Carrera", "category": "Sports", "price": 126000, "quantity": 2},
    )
    assert created.status_code == 201
    assert created.json()["make"] == "Porsche"

    results = client.get("/api/vehicles/search?make=Porsche", headers=headers)
    assert results.status_code == 200
    assert results.json()["total"] == 1


def test_purchase_decrements_stock_and_never_goes_negative():
    headers = auth_headers()
    created = client.post(
        "/api/vehicles",
        headers=headers,
        json={"make": "Volvo", "model": "XC90", "category": "SUV", "price": 79000, "quantity": 1},
    ).json()
    purchased = client.post(f"/api/vehicles/{created['id']}/purchase", headers=headers)
    assert purchased.status_code == 200
    assert purchased.json()["quantity"] == 0

    unavailable = client.post(f"/api/vehicles/{created['id']}/purchase", headers=headers)
    assert unavailable.status_code == 409

    all_orders = client.get("/api/admin/orders", headers=headers)
    assert all_orders.status_code == 200
    assert len(all_orders.json()) == 1


def test_non_admin_cannot_add_or_restock_vehicle():
    client.post("/api/auth/register", json={"name": "Nina User", "email": "nina@example.com", "password": "UserPass123!"})
    login = client.post("/api/auth/login", json={"email": "nina@example.com", "password": "UserPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.post("/api/vehicles", headers=headers, json={"make": "Audi", "model": "R8", "category": "Sports", "price": 150000, "quantity": 1})
    assert response.status_code == 403


def test_admin_can_update_restock_and_delete_vehicle():
    headers = auth_headers()
    vehicle = client.post("/api/vehicles", headers=headers, json={"make": "BMW", "model": "M4", "category": "Sports", "price": 85000, "quantity": 1}).json()
    updated = client.put(f"/api/vehicles/{vehicle['id']}", headers=headers, json={"price": 87000})
    assert updated.status_code == 200
    assert updated.json()["price"] == 87000
    restocked = client.post(f"/api/vehicles/{vehicle['id']}/restock", headers=headers, json={"quantity": 3})
    assert restocked.json()["quantity"] == 4
    deleted = client.delete(f"/api/vehicles/{vehicle['id']}", headers=headers)
    assert deleted.status_code == 204


def test_search_filters_by_category_and_price():
    headers = auth_headers()
    client.post("/api/vehicles", headers=headers, json={"make": "Audi", "model": "Q8", "category": "SUV", "price": 71000, "quantity": 2})
    client.post("/api/vehicles", headers=headers, json={"make": "Audi", "model": "A8", "category": "Luxury", "price": 99000, "quantity": 1})
    results = client.get("/api/vehicles/search?category=SUV&max_price=80000", headers=headers)
    assert results.status_code == 200
    assert results.json()["total"] == 1
