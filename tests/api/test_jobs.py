from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_list_jobs_returns_items() -> None:
    response = client.get("/api/v1/jobs")

    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] >= 1
    assert len(payload["items"]) >= 1


def test_list_jobs_filters_by_query() -> None:
    response = client.get("/api/v1/jobs", params={"q": "sales"})

    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["job_name"] == "sales_orders_pipeline"


def test_get_job_incidents() -> None:
    response = client.get("/api/v1/jobs/12345/incidents")

    assert response.status_code == 200

    payload = response.json()
    assert payload["job_id"] == "12345"
    assert payload["latest_status"] == "failed"
    assert len(payload["recent_incidents"]) == 2


def test_get_job_incidents_unknown_job() -> None:
    response = client.get("/api/v1/jobs/unknown/incidents")

    assert response.status_code == 200

    payload = response.json()
    assert payload["job_id"] == "unknown"
    assert payload["recent_incidents"] == []
