from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_get_lineage_detail() -> None:
    response = client.get("/api/v1/lineage/main.sales.orders")

    assert response.status_code == 200

    payload = response.json()
    assert payload["dataset_id"] == "main.sales.orders"
    assert "main.raw.orders_source" in payload["upstream"]
    assert "main.gold.sales_kpis" in payload["downstream"]
    assert "sales_orders_pipeline" in payload["related_jobs"]


def test_get_lineage_unknown_dataset() -> None:
    response = client.get("/api/v1/lineage/unknown.dataset")

    assert response.status_code == 200

    payload = response.json()
    assert payload["dataset_id"] == "unknown.dataset"
    assert payload["upstream"] == []
    assert payload["downstream"] == []
    assert payload["related_jobs"] == []
