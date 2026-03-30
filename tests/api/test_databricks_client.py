from app.api.clients.databricks_client import DatabricksClient


def test_databricks_client_is_not_configured_by_default() -> None:
    client = DatabricksClient()

    assert client.is_configured() is False
    assert client.get_tables() == []
    assert client.get_jobs() == []
    assert client.get_job_runs() == []
    assert client.get_lineage() == []


def test_get_tables_calls_unity_catalog_when_client_is_configured(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"
    client.catalog = "main"

    def fake_get(path: str, params=None):
        assert path == "/api/2.1/unity-catalog/tables"
        assert params == {"catalog_name": "main"}
        return {
            "tables": [
                {
                    "full_name": "main.sales.orders",
                    "catalog_name": "main",
                    "schema_name": "sales",
                    "name": "orders",
                    "table_type": "MANAGED",
                    "comment": "Orders table",
                    "owner": "sales-platform",
                }
            ]
        }

    monkeypatch.setattr(client, "_get", fake_get)

    tables = client.get_tables()

    assert tables == [
        {
            "dataset_id": "main.sales.orders",
            "name": "main.sales.orders",
            "catalog": "main",
            "schema": "sales",
            "table": "orders",
            "type": "managed",
            "description": "Orders table",
            "owner": "sales-platform",
            "columns": [],
            "documentation": [],
        }
    ]


def test_get_tables_builds_full_name_when_missing(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"
    client.catalog = "main"

    def fake_get(path: str, params=None):
        return {
            "tables": [
                {
                    "catalog_name": "main",
                    "schema_name": "finance",
                    "name": "invoices",
                    "table_type": "EXTERNAL",
                    "comment": "Invoices table",
                    "owner": "finance-data",
                }
            ]
        }

    monkeypatch.setattr(client, "_get", fake_get)

    tables = client.get_tables()

    assert tables == [
        {
            "dataset_id": "main.finance.invoices",
            "name": "main.finance.invoices",
            "catalog": "main",
            "schema": "finance",
            "table": "invoices",
            "type": "external",
            "description": "Invoices table",
            "owner": "finance-data",
            "columns": [],
            "documentation": [],
        }
    ]


def test_get_jobs_calls_databricks_jobs_api(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"

    def fake_get(path: str, params=None):
        assert path == "/api/2.1/jobs/list"
        assert params is None
        return {
            "jobs": [
                {
                    "job_id": 12345,
                    "settings": {
                        "name": "sales_orders_pipeline",
                    },
                }
            ]
        }

    monkeypatch.setattr(client, "_get", fake_get)

    jobs = client.get_jobs()

    assert jobs == [
        {
            "job_id": "12345",
            "job_name": "sales_orders_pipeline",
            "status": "active",
        }
    ]


def test_get_job_runs_calls_databricks_runs_api(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"

    def fake_get(path: str, params=None):
        assert path == "/api/2.1/jobs/runs/list"
        assert params == {"limit": "25"}
        return {
            "runs": [
                {
                    "run_id": 98765,
                    "job_id": 12345,
                    "start_time": 1711792800000,
                    "end_time": 1711793100000,
                    "state": {
                        "life_cycle_state": "TERMINATED",
                        "result_state": "FAILED",
                        "state_message": "Cluster terminated before task completion",
                    },
                }
            ]
        }

    monkeypatch.setattr(client, "_get", fake_get)

    runs = client.get_job_runs()

    assert runs == [
        {
            "run_id": "98765",
            "job_id": "12345",
            "lifecycle_state": "TERMINATED",
            "result_state": "FAILED",
            "state_message": "Cluster terminated before task completion",
            "start_time": "1711792800000",
            "end_time": "1711793100000",
        }
    ]


def test_get_lineage_calls_databricks_lineage_api(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"
    client.catalog = "main"

    def fake_get(path: str, params=None):
        assert path == "/api/2.1/unity-catalog/table-lineage"
        assert params == {"catalog_name": "main"}
        return {
            "lineage": [
                {
                    "table_info": {
                        "full_name": "main.sales.orders",
                    },
                    "upstreams": [
                        {
                            "table_info": {
                                "full_name": "main.raw.orders_source",
                            }
                        }
                    ],
                    "downstreams": [
                        {
                            "table_info": {
                                "full_name": "main.gold.sales_kpis",
                            }
                        }
                    ],
                    "jobs": [
                        {
                            "job_name": "sales_orders_pipeline",
                        }
                    ],
                }
            ]
        }

    monkeypatch.setattr(client, "_get", fake_get)

    lineage = client.get_lineage()

    assert lineage == [
        {
            "dataset_id": "main.sales.orders",
            "upstream": ["main.raw.orders_source"],
            "downstream": ["main.gold.sales_kpis"],
            "related_jobs": ["sales_orders_pipeline"],
        }
    ]
