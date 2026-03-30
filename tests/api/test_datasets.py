import os

from fastapi.testclient import TestClient

os.environ["DATABRICKS_HOST"] = ""
os.environ["DATABRICKS_TOKEN"] = ""

from app.api.main import app

client = TestClient(app)


def test_list_datasets_returns_items() -> None:
    response = client.get("/api/v1/datasets")

    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] >= 1
    assert len(payload["items"]) >= 1


def test_list_datasets_filters_by_query() -> None:
    response = client.get("/api/v1/datasets", params={"q": "orders"})

    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["dataset_id"] == "main.sales.orders"


def test_get_dataset_detail() -> None:
    response = client.get("/api/v1/datasets/main.sales.orders")

    assert response.status_code == 200

    payload = response.json()
    assert payload["dataset_id"] == "main.sales.orders"
    assert payload["owner"] == "sales-platform"
    assert len(payload["columns"]) == 3
