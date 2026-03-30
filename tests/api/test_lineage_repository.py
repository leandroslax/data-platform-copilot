from app.api.repositories import lineage_repository


def test_find_lineage_uses_mock_data_when_databricks_is_not_configured(monkeypatch) -> None:
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


def test_find_lineage_falls_back_to_mock_when_databricks_returns_no_records(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_lineage(self):
            return []

    monkeypatch.setattr(lineage_repository, "DatabricksClient", StubDatabricksClient)

    lineage = lineage_repository.find_lineage_by_dataset_id("main.sales.orders")

    assert lineage is not None
    assert lineage["dataset_id"] == "main.sales.orders"
    assert "main.raw.orders_source" in lineage["upstream"]


def test_find_lineage_uses_databricks_when_records_exist(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_lineage(self):
            return [
                {
                    "dataset_id": "samples.tpch.orders",
                    "upstream": ["samples.tpch.customer"],
                    "downstream": ["analytics.gold.orders_enriched"],
                    "related_jobs": ["tpch_orders_pipeline"],
                }
            ]

    monkeypatch.setattr(lineage_repository, "DatabricksClient", StubDatabricksClient)

    lineage = lineage_repository.find_lineage_by_dataset_id("samples.tpch.orders")

    assert lineage is not None
    assert lineage == {
        "dataset_id": "samples.tpch.orders",
        "upstream": ["samples.tpch.customer"],
        "downstream": ["analytics.gold.orders_enriched"],
        "related_jobs": ["tpch_orders_pipeline"],
    }
