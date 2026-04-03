import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.api.clients.bigquery_client import BigQueryClient
from app.api.clients.databricks_client import DatabricksClient
from app.api.core.config import settings
from app.api.services.mock_data import DATASETS


def _normalize_dataset_record(dataset: Dict[str, Any]) -> Dict[str, Any]:
    catalog = dataset.get("catalog")
    schema_name = dataset.get("schema") or dataset.get("schema_name")
    table = dataset.get("table")
    dataset_name = dataset.get("name")
    dataset_id = dataset.get("dataset_id")

    if not dataset_id and catalog and schema_name and table:
        dataset_id = f"{catalog}.{schema_name}.{table}"

    if not dataset_name:
        dataset_name = dataset_id or table or "unknown"

    normalized = deepcopy(dataset)
    normalized["dataset_id"] = dataset_id or dataset_name
    normalized["name"] = dataset_name
    normalized["catalog"] = catalog
    normalized["schema"] = schema_name
    normalized["table"] = table
    normalized["type"] = dataset.get("type", "table")
    normalized["columns"] = dataset.get("columns", [])
    normalized["documentation"] = dataset.get("documentation", [])
    normalized["owner"] = dataset.get("owner")
    normalized["description"] = dataset.get("description")
    normalized["source_system"] = dataset.get("source_system")

    return normalized


def _read_persisted_catalog() -> List[Dict[str, Any]]:
    catalog_path = Path(settings.metadata_catalog_path)
    if not catalog_path.exists():
        return []

    try:
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    return [_normalize_dataset_record(dataset) for dataset in payload.get("datasets", [])]


def _list_bigquery_catalog_datasets() -> List[Dict[str, Any]]:
    try:
        client = BigQueryClient()
    except Exception:
        return []

    datasets: List[Dict[str, Any]] = []
    dataset_names = [settings.novadrive_silver_dataset, settings.novadrive_gold_dataset]

    for dataset_name in dataset_names:
        try:
            tables = client.list_tables(dataset_name)
        except Exception:
            continue

        for table in tables:
            datasets.append(
                _normalize_dataset_record(
                    {
                        **table,
                        "owner": table.get("owner") or settings.metadata_owner_default,
                        "source_system": "bigquery",
                    }
                )
            )

    return datasets


def list_live_datasets() -> List[Dict[str, Any]]:
    client = DatabricksClient()
    datasets: List[Dict[str, Any]] = []

    if client.is_configured():
        tables = client.get_tables()
        if tables:
            datasets.extend(
                [
                    _normalize_dataset_record({**dataset, "source_system": "databricks"})
                    for dataset in tables
                ]
            )

    if not datasets:
        datasets.extend(
            [_normalize_dataset_record({**dataset, "source_system": "mock"}) for dataset in DATASETS]
        )

    datasets.extend(_list_bigquery_catalog_datasets())

    deduplicated: Dict[str, Dict[str, Any]] = {}
    for dataset in datasets:
        deduplicated[dataset["dataset_id"]] = dataset

    return list(deduplicated.values())


def list_datasets() -> List[Dict[str, Any]]:
    persisted = _read_persisted_catalog()
    return persisted or list_live_datasets()


def find_dataset_by_id(dataset_id: str) -> Optional[Dict[str, Any]]:
    for dataset in _read_persisted_catalog():
        if dataset["dataset_id"] == dataset_id:
            return dataset

    client = DatabricksClient()

    if client.is_configured():
        dataset = client.get_table(dataset_id)
        if dataset:
            return _normalize_dataset_record(dataset)

    bigquery_client = BigQueryClient()
    dataset = bigquery_client.get_table(dataset_id)
    if dataset:
        return _normalize_dataset_record(dataset)

    for dataset in list_live_datasets():
        if dataset["dataset_id"] == dataset_id:
            return dataset
    return None
