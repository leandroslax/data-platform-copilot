import json
import math
from pathlib import Path
from typing import Any

from app.api.core.config import settings
from app.api.repositories.dataset_repository import list_datasets
from app.api.services.embedding_service import embed_text
from app.api.services.metadata_catalog_service import refresh_metadata_catalog


def _catalog_snapshot_path() -> Path:
    return Path(settings.metadata_catalog_path)


def _embedding_index_path() -> Path:
    return Path(settings.metadata_embedding_index_path)


def _load_catalog_snapshot() -> dict[str, Any]:
    snapshot_path = _catalog_snapshot_path()
    if not snapshot_path.exists():
        refresh_metadata_catalog()

    try:
        return json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        refresh_metadata_catalog()
        return json.loads(snapshot_path.read_text(encoding="utf-8"))


def _load_embedding_index() -> dict[str, Any]:
    index_path = _embedding_index_path()
    if not index_path.exists():
        refresh_metadata_catalog()

    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        refresh_metadata_catalog()
        return json.loads(index_path.read_text(encoding="utf-8"))


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot_product / (left_norm * right_norm)


def search_catalog(query: str, limit: int | None = None) -> list[dict[str, Any]]:
    search_limit = limit or settings.retrieval_result_limit
    query_embedding = embed_text(query)
    index = _load_embedding_index()
    snapshot = _load_catalog_snapshot()
    datasets_by_id = {dataset["dataset_id"]: dataset for dataset in list_datasets()}
    documents_by_id = {document["item_id"]: document for document in snapshot.get("documents", [])}

    scored_items = []
    for item in index.get("items", []):
        score = _cosine_similarity(query_embedding, item.get("embedding", []))
        item_type = item.get("item_type", "dataset")

        if item_type == "document":
            document = documents_by_id.get(item["item_id"])
            if document is None:
                continue
            context = {
                "item_type": "document",
                "item_id": document["item_id"],
                "name": document["name"],
                "description": document.get("description"),
                "path": document.get("path"),
                "source_system": document.get("source_system"),
            }
        else:
            dataset = datasets_by_id.get(item["dataset_id"])
            if dataset is None:
                continue
            context = {
                "item_type": "dataset",
                **dataset,
            }

        scored_items.append(
            {
                "item_id": item["item_id"],
                "item_type": item_type,
                "dataset_id": item.get("dataset_id"),
                "name": item.get("name") or item.get("dataset_id") or item["item_id"],
                "owner": item.get("owner"),
                "description": item.get("description"),
                "source_system": item.get("source_system"),
                "path": item.get("path"),
                "score": round(score, 4),
                "context": context,
            }
        )

    scored_items.sort(key=lambda item: item["score"], reverse=True)
    return scored_items[:search_limit]


def summarize_owners() -> list[dict[str, Any]]:
    owner_counts: dict[str, int] = {}
    for dataset in list_datasets():
        owner = dataset.get("owner") or settings.metadata_owner_default
        owner_counts[owner] = owner_counts.get(owner, 0) + 1

    summary = [{"owner": owner, "dataset_count": count} for owner, count in owner_counts.items()]
    summary.sort(key=lambda item: (-item["dataset_count"], item["owner"]))
    return summary
