from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.api.clients.databricks_client import DatabricksClient
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

    return normalized


def _get_dataset_source() -> List[Dict[str, Any]]:
    client = DatabricksClient()

    if client.is_configured():
        tables = client.get_tables()
        if tables:
            return [_normalize_dataset_record(dataset) for dataset in tables]

    return [_normalize_dataset_record(dataset) for dataset in DATASETS]


def list_datasets() -> List[Dict[str, Any]]:
    return _get_dataset_source()


def find_dataset_by_id(dataset_id: str) -> Optional[Dict[str, Any]]:
    for dataset in _get_dataset_source():
        if dataset["dataset_id"] == dataset_id:
            return dataset
    return None
