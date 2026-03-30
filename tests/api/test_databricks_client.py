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
