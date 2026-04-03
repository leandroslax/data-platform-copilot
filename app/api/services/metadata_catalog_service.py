import glob
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


def _repo_root() -> Path:
    return _catalog_snapshot_path().resolve().parents[3]


def _document_patterns() -> list[str]:
    return [pattern.strip() for pattern in settings.metadata_document_globs.split(",") if pattern.strip()]


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


def _extract_document_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return path.stem.replace("-", " ").replace("_", " ").title()


def _extract_document_summary(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:240]
    return None


def _collect_documents() -> list[dict[str, Any]]:
    repo_root = _repo_root()
    documents: list[dict[str, Any]] = []
    seen_paths: set[str] = set()

    for pattern in _document_patterns():
        for matched_path in sorted(glob.glob(str(repo_root / pattern), recursive=True)):
            path = Path(matched_path)
            if not path.is_file():
                continue

            resolved = str(path.resolve())
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)

            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue

            relative_path = str(path.relative_to(repo_root))
            title = _extract_document_title(content, path)
            summary = _extract_document_summary(content)
            retrieval_text = " | ".join(
                part
                for part in [
                    title,
                    f"path {relative_path}",
                    summary,
                    content[:2000].replace("\n", " "),
                ]
                if part
            )

            documents.append(
                {
                    "item_id": f"document:{relative_path}",
                    "item_type": "document",
                    "dataset_id": None,
                    "name": title,
                    "owner": None,
                    "description": summary,
                    "source_system": "repo-docs",
                    "path": relative_path,
                    "retrieval_text": retrieval_text,
                }
            )

    return documents


def _enrich_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(dataset)
    if not enriched.get("owner"):
        enriched["owner"] = settings.metadata_owner_default

    enriched["retrieval_text"] = _build_retrieval_text(enriched)
    return enriched


def refresh_metadata_catalog() -> dict[str, Any]:
    datasets = [_enrich_dataset(dataset) for dataset in list_live_datasets()]
    documents = _collect_documents()
    generated_at = datetime.now(UTC).isoformat()

    snapshot_path = _catalog_snapshot_path()
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "dataset_count": len(datasets),
                "document_count": len(documents),
                "datasets": datasets,
                "documents": documents,
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )

    embedding_items = [
        {
            "item_id": dataset["dataset_id"],
            "item_type": "dataset",
            "dataset_id": dataset["dataset_id"],
            "name": dataset["name"],
            "owner": dataset.get("owner"),
            "description": dataset.get("description"),
            "source_system": dataset.get("source_system"),
            "path": None,
            "retrieval_text": dataset["retrieval_text"],
            "embedding": embed_text(dataset["retrieval_text"]),
        }
        for dataset in datasets
    ]
    embedding_items.extend(
        {
            "item_id": document["item_id"],
            "item_type": "document",
            "dataset_id": None,
            "name": document["name"],
            "owner": None,
            "description": document.get("description"),
            "source_system": document.get("source_system"),
            "path": document.get("path"),
            "retrieval_text": document["retrieval_text"],
            "embedding": embed_text(document["retrieval_text"]),
        }
        for document in documents
    )

    embedding_index_path = _embedding_index_path()
    embedding_index_path.parent.mkdir(parents=True, exist_ok=True)
    embedding_index_path.write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "dataset_count": len(datasets),
                "document_count": len(documents),
                "items": embedding_items,
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )

    return {
        "dataset_count": len(datasets),
        "document_count": len(documents),
        "generated_at": generated_at,
        "snapshot_path": str(snapshot_path),
        "embedding_index_path": str(embedding_index_path),
    }
