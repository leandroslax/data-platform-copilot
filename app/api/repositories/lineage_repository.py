from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.api.clients.databricks_client import DatabricksClient
from app.api.services.mock_data import LINEAGE


def _normalize_lineage_record(lineage: Dict[str, Any]) -> Dict[str, Any]:
    dataset_id = (
        lineage.get("dataset_id")
        or lineage.get("entity_id")
        or lineage.get("table_name")
        or ""
    )

    upstream = lineage.get("upstream") or lineage.get("upstreams") or []
    downstream = lineage.get("downstream") or lineage.get("downstreams") or []
    related_jobs = lineage.get("related_jobs") or lineage.get("jobs") or []

    normalized = deepcopy(lineage)
    normalized["dataset_id"] = dataset_id
    normalized["upstream"] = list(upstream)
    normalized["downstream"] = list(downstream)
    normalized["related_jobs"] = list(related_jobs)

    return normalized


def _get_lineage_source() -> List[Dict[str, Any]]:
    client = DatabricksClient()

    if client.is_configured():
        return [_normalize_lineage_record(lineage) for lineage in client.get_lineage()]

    return [_normalize_lineage_record(lineage) for lineage in LINEAGE.values()]


def find_lineage_by_dataset_id(dataset_id: str) -> Optional[Dict[str, Any]]:
    for lineage in _get_lineage_source():
        if lineage["dataset_id"] == dataset_id:
            return lineage
    return None
