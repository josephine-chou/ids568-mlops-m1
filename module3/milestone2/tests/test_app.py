import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Iris Classification API is running"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_predict_valid():
    payload = {
        "features": [5.1, 3.5, 1.4, 0.2]
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "class_name" in data
    assert "probabilities" in data
    assert data["prediction"] in [0, 1, 2]
    assert len(data["probabilities"]) == 3