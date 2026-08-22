from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def auth_headers():
    client.post(
        "/api/auth/register",
        json={"name": "Ava Admin", "email": "admin@example.com", "password": "AdminPass123!", "role": "admin"},
    )
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
