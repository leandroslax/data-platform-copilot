from app.api.repositories import dataset_repository


def test_list_datasets_uses_mock_data_when_databricks_is_not_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return False

        def get_tables(self):
            return [
                {
                    "dataset_id": "main.should.not.appear",
                    "name": "main.should.not.appear",
                }
            ]

    monkeypatch.setattr(dataset_repository, "DatabricksClient", StubDatabricksClient)

    datasets = dataset_repository.list_datasets()

    assert len(datasets) == 2
    assert datasets[0]["dataset_id"] == "main.sales.orders"


def test_list_datasets_uses_databricks_when_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_tables(self):
            return [
                {
                    "catalog": "analytics",
                    "schema_name": "gold",
                    "table": "customer_kpis",
                    "description": "Gold KPI table",
                    "owner": "analytics-team",
                    "columns": [
                        {
                            "name": "customer_id",
                            "data_type": "string",
                            "nullable": False,
                        }
                    ],
                }
            ]

    monkeypatch.setattr(dataset_repository, "DatabricksClient", StubDatabricksClient)

    datasets = dataset_repository.list_datasets()

    assert datasets == [
        {
            "catalog": "analytics",
            "schema_name": "gold",
            "table": "customer_kpis",
            "description": "Gold KPI table",
            "owner": "analytics-team",
            "columns": [
                {
                    "name": "customer_id",
                    "data_type": "string",
                    "nullable": False,
                }
            ],
            "dataset_id": "analytics.gold.customer_kpis",
            "name": "analytics.gold.customer_kpis",
            "schema": "gold",
            "type": "table",
            "documentation": [],
        }
    ]


def test_find_dataset_by_id_reads_from_databricks_when_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_tables(self):
            return [
                {
                    "dataset_id": "analytics.silver.customers",
                    "name": "analytics.silver.customers",
                    "catalog": "analytics",
                    "schema": "silver",
                    "table": "customers",
                    "type": "view",
                }
            ]

    monkeypatch.setattr(dataset_repository, "DatabricksClient", StubDatabricksClient)

    dataset = dataset_repository.find_dataset_by_id("analytics.silver.customers")

    assert dataset is not None
    assert dataset["type"] == "view"
