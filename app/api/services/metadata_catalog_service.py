import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.api.core.config import settings
from app.api.repositories.dataset_repository import list_live_datasets
from app.api.services.embedding_service import embed_text


def _catalog_snapshot_path() -> Path:
    return Path(settings.metadata_catalog_path)


def _embedding_index_path() -> Path:
    return Path(settings.metadata_embedding_index_path)


def _build_retrieval_text(dataset: dict[str, Any]) -> str:
    column_names = ", ".join(column.get("name", "") for column in dataset.get("columns", [])[:20])
    return " | ".join(
        part
        for part in [
            dataset.get("dataset_id"),
            dataset.get("description"),
            f"owner {dataset.get('owner')}" if dataset.get("owner") else None,
            f"catalog {dataset.get('catalog')}" if dataset.get("catalog") else None,
            f"schema {dataset.get('schema')}" if dataset.get("schema") else None,
            f"columns {column_names}" if column_names else None,
            f"source {dataset.get('source_system')}" if dataset.get("source_system") else None,
        ]
        if part
    )


def _enrich_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(dataset)
    if not enriched.get("owner"):
        enriched["owner"] = settings.metadata_owner_default

    enriched["retrieval_text"] = _build_retrieval_text(enriched)
    return enriched


def refresh_metadata_catalog() -> dict[str, Any]:
    datasets = [_enrich_dataset(dataset) for dataset in list_live_datasets()]
    generated_at = datetime.now(UTC).isoformat()

    snapshot_path = _catalog_snapshot_path()
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "dataset_count": len(datasets),
                "datasets": datasets,
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )

    embedding_items = [
        {
            "dataset_id": dataset["dataset_id"],
            "name": dataset["name"],
            "owner": dataset.get("owner"),
            "description": dataset.get("description"),
            "source_system": dataset.get("source_system"),
            "retrieval_text": dataset["retrieval_text"],
            "embedding": embed_text(dataset["retrieval_text"]),
        }
        for dataset in datasets
    ]

    embedding_index_path = _embedding_index_path()
    embedding_index_path.parent.mkdir(parents=True, exist_ok=True)
    embedding_index_path.write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "dataset_count": len(embedding_items),
                "items": embedding_items,
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )

    return {
        "dataset_count": len(datasets),
        "generated_at": generated_at,
        "snapshot_path": str(snapshot_path),
        "embedding_index_path": str(embedding_index_path),
    }
