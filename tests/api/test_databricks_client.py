from urllib.error import HTTPError

from app.api.clients.databricks_client import DatabricksClient


def test_databricks_client_is_not_configured_by_default() -> None:
    client = DatabricksClient()
    client.host = ""
    client.token = ""

    assert client.is_configured() is False
    assert client.get_tables() == []
    assert client.get_jobs() == []
    assert client.get_job_runs() == []
    assert client.get_lineage() == []


def test_get_tables_lists_schemas_then_tables(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"
    client.catalog = "workspace"

    def fake_get(path: str, params=None):
        if path == "/api/2.1/unity-catalog/schemas":
            assert params == {"catalog_name": "workspace"}
            return {
                "schemas": [
                    {"name": "default"},
                    {"name": "information_schema"},
                ]
            }

        if path == "/api/2.1/unity-catalog/tables":
            assert params == {
                "catalog_name": "workspace",
                "schema_name": "default",
            }
            return {
                "tables": [
                    {
                        "full_name": "workspace.default.sales_orders",
                        "catalog_name": "workspace",
                        "schema_name": "default",
                        "name": "sales_orders",
                        "table_type": "MANAGED",
                        "comment": "Orders table",
                        "owner": "sales-platform",
                    }
                ]
            }

        raise AssertionError(f"Unexpected path: {path}")

    monkeypatch.setattr(client, "_get", fake_get)

    tables = client.get_tables()

    assert tables == [
        {
            "dataset_id": "workspace.default.sales_orders",
            "name": "workspace.default.sales_orders",
            "catalog": "workspace",
            "schema": "default",
            "table": "sales_orders",
            "type": "managed",
            "description": "Orders table",
            "owner": "sales-platform",
            "columns": [],
            "documentation": [],
        }
    ]


def test_get_table_returns_table_detail(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"
    client.catalog = "samples"

    def fake_get(path: str, params=None):
        assert path == "/api/2.1/unity-catalog/tables/samples.tpch.orders"
        return {
            "full_name": "samples.tpch.orders",
            "catalog_name": "samples",
            "schema_name": "tpch",
            "name": "orders",
            "table_type": "MANAGED",
            "comment": "Orders",
            "owner": "System user",
            "columns": [
                {
                    "name": "o_orderkey",
                    "type_text": "bigint",
                    "type_json": '{"name":"o_orderkey"}',
                    "comment": "Order key",
                }
            ],
        }

    monkeypatch.setattr(client, "_get", fake_get)

    table = client.get_table("samples.tpch.orders")

    assert table == {
        "dataset_id": "samples.tpch.orders",
        "name": "samples.tpch.orders",
        "catalog": "samples",
        "schema": "tpch",
        "table": "orders",
        "type": "managed",
        "description": "Orders",
        "owner": "System user",
        "columns": [
            {
                "name": "o_orderkey",
                "data_type": "bigint",
                "nullable": True,
                "description": "Order key",
            }
        ],
        "documentation": [],
    }


def test_get_tables_returns_empty_on_http_error(monkeypatch) -> None:
    client = DatabricksClient()
    client.host = "https://example.cloud.databricks.com"
    client.token = "token"
    client.catalog = "workspace"

    def fake_get(path: str, params=None):
        raise HTTPError("https://example.com", 400, "Bad Request", hdrs=None, fp=None)

    monkeypatch.setattr(client, "_get", fake_get)

    assert client.get_tables() == []


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
