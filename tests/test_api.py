"""API endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_black_scholes_endpoint() -> None:
    client = TestClient(app)
    payload = {
        "spot": 100.0,
        "strike": 100.0,
        "rate": 0.05,
        "volatility": 0.2,
        "maturity": 1.0,
        "option_type": "call",
    }
    response = client.post("/price/black-scholes", json=payload)
    assert response.status_code == 200
    assert response.json()["price"] > 0.0


def test_validation_rejects_negative_spot() -> None:
    client = TestClient(app)
    payload = {
        "spot": -1.0,
        "strike": 100.0,
        "rate": 0.05,
        "volatility": 0.2,
        "maturity": 1.0,
        "option_type": "call",
    }
    response = client.post("/price/black-scholes", json=payload)
    assert response.status_code == 422
