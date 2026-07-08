import os
# Force testing to use local SQLite database
os.environ["DATABASE_URL"] = "sqlite:///tests/test_api_history.db"

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/history?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]

def test_api_scan_username():
    response = client.post("/api/scan/username", json={"username": "testuser"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_api_scan_email():
    response = client.post("/api/scan/email", json={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
