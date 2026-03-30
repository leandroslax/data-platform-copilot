from app.api.clients.databricks_client import DatabricksClient


def test_databricks_client_is_not_configured_by_default() -> None:
    client = DatabricksClient()

    assert client.is_configured() is False
    assert client.get_tables() == []
    assert client.get_jobs() == []
    assert client.get_job_runs() == []
    assert client.get_lineage() == []
