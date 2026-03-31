from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_faturamento_concessionarias_endpoint() -> None:
    response = client.get("/api/v1/novadrive/faturamento/concessionarias")

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert "limit" in payload


def test_performance_vendedores_endpoint() -> None:
    response = client.get("/api/v1/novadrive/performance/vendedores")

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert "limit" in payload
