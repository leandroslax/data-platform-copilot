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


def test_find_dataset_by_id_reads_detail_from_databricks_when_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_table(self, dataset_id: str):
            if dataset_id != "samples.tpch.orders":
                return None

            return {
                "dataset_id": "samples.tpch.orders",
                "name": "samples.tpch.orders",
                "catalog": "samples",
                "schema": "tpch",
                "table": "orders",
                "type": "managed",
                "description": "Orders table",
                "owner": "System user",
                "columns": [
                    {
                        "name": "o_orderkey",
                        "data_type": "bigint",
                        "nullable": True,
                        "description": None,
                    }
                ],
                "documentation": [],
            }

        def get_tables(self):
            return []

    monkeypatch.setattr(dataset_repository, "DatabricksClient", StubDatabricksClient)

    dataset = dataset_repository.find_dataset_by_id("samples.tpch.orders")

    assert dataset is not None
    assert dataset["dataset_id"] == "samples.tpch.orders"
    assert dataset["columns"][0]["name"] == "o_orderkey"


def test_find_dataset_by_id_reads_detail_from_bigquery_when_databricks_does_not_match(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return False

        def get_tables(self):
            return []

    class StubBigQueryClient:
        def get_table(self, dataset_id: str):
            if dataset_id != "data-platform-copilot-dev.silver_novadrive.vendas":
                return None

            return {
                "dataset_id": dataset_id,
                "name": dataset_id,
                "catalog": "data-platform-copilot-dev",
                "schema": "silver_novadrive",
                "table": "vendas",
                "type": "table",
                "description": "Tabela silver de vendas",
                "owner": None,
                "columns": [
                    {
                        "name": "id_venda",
                        "data_type": "INT64",
                        "nullable": False,
                        "description": None,
                    }
                ],
                "documentation": [],
            }

    monkeypatch.setattr(dataset_repository, "DatabricksClient", StubDatabricksClient)
    monkeypatch.setattr(dataset_repository, "BigQueryClient", StubBigQueryClient)

    dataset = dataset_repository.find_dataset_by_id("data-platform-copilot-dev.silver_novadrive.vendas")

    assert dataset is not None
    assert dataset["dataset_id"] == "data-platform-copilot-dev.silver_novadrive.vendas"
    assert dataset["schema"] == "silver_novadrive"
    assert dataset["columns"][0]["name"] == "id_venda"
