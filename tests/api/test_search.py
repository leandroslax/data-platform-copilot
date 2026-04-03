import os

from fastapi.testclient import TestClient

os.environ["DATABRICKS_HOST"] = ""
os.environ["DATABRICKS_TOKEN"] = ""

from app.api.main import app
from app.api.routes import metadata as metadata_route
from app.api.routes import search as search_route

client = TestClient(app)


def test_search_route_returns_semantic_results(monkeypatch) -> None:
    monkeypatch.setattr(
        search_route,
        "search_catalog",
        lambda query, limit: [
            {
                "dataset_id": "main.sales.orders",
                "name": "main.sales.orders",
                "owner": "sales-platform",
                "description": "Orders",
                "source_system": "mock",
                "score": 0.92,
            }
        ],
    )

    response = client.get("/api/v1/search", params={"q": "orders"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["dataset_id"] == "main.sales.orders"


def test_metadata_sync_route_returns_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        metadata_route,
        "refresh_metadata_catalog",
        lambda: {
            "dataset_count": 3,
            "generated_at": "2026-04-02T23:00:00Z",
            "snapshot_path": "pipelines/metadata/state/catalog_snapshot.json",
            "embedding_index_path": "pipelines/metadata/state/catalog_embeddings.json",
        },
    )

    response = client.post("/api/v1/metadata/sync")

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_count"] == 3
    assert payload["snapshot_path"].endswith("catalog_snapshot.json")
