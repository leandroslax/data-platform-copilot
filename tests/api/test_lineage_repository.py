from app.api.repositories import lineage_repository


def test_find_lineage_by_dataset_id_uses_mock_data_when_databricks_is_not_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return False

        def get_lineage(self):
            return [
                {
                    "dataset_id": "should.not.appear",
                    "upstream": ["x"],
                    "downstream": ["y"],
                    "related_jobs": ["z"],
                }
            ]

    monkeypatch.setattr(lineage_repository, "DatabricksClient", StubDatabricksClient)

    lineage = lineage_repository.find_lineage_by_dataset_id("main.sales.orders")

    assert lineage is not None
    assert lineage["dataset_id"] == "main.sales.orders"
    assert "main.raw.orders_source" in lineage["upstream"]


def test_find_lineage_by_dataset_id_uses_databricks_when_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_lineage(self):
            return [
                {
                    "entity_id": "analytics.gold.customer_kpis",
                    "upstreams": ["analytics.silver.customers"],
                    "downstreams": ["analytics.serving.customer_metrics"],
                    "jobs": ["customer_kpi_refresh"],
                }
            ]

    monkeypatch.setattr(lineage_repository, "DatabricksClient", StubDatabricksClient)

    lineage = lineage_repository.find_lineage_by_dataset_id("analytics.gold.customer_kpis")

    assert lineage is not None
    assert lineage["dataset_id"] == "analytics.gold.customer_kpis"
    assert lineage["upstream"] == ["analytics.silver.customers"]
    assert lineage["downstream"] == ["analytics.serving.customer_metrics"]
    assert lineage["related_jobs"] == ["customer_kpi_refresh"]


def test_find_lineage_by_dataset_id_returns_none_when_not_found(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_lineage(self):
            return []

    monkeypatch.setattr(lineage_repository, "DatabricksClient", StubDatabricksClient)

    lineage = lineage_repository.find_lineage_by_dataset_id("unknown.dataset")

    assert lineage is None
