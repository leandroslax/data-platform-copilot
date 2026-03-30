from typing import Optional

from app.api.repositories.dataset_repository import find_dataset_by_id, list_datasets as list_dataset_records
from app.api.schemas.datasets import (
    DatasetColumn,
    DatasetDetailResponse,
    DatasetDocument,
    DatasetItem,
    DatasetListResponse,
)


def list_datasets(
    q: Optional[str],
    catalog: Optional[str],
    schema: Optional[str],
    owner: Optional[str],
    limit: int,
) -> DatasetListResponse:
    filtered = list_dataset_records()

    if q:
        query = q.lower()
        filtered = [
            dataset
            for dataset in filtered
            if query in dataset["name"].lower()
            or query in (dataset.get("description") or "").lower()
        ]

    if catalog:
        filtered = [
            dataset for dataset in filtered if dataset["catalog"].lower() == catalog.lower()
        ]

    if schema:
        filtered = [
            dataset for dataset in filtered if dataset["schema"].lower() == schema.lower()
        ]

    if owner:
        filtered = [
            dataset for dataset in filtered if (dataset.get("owner") or "").lower() == owner.lower()
        ]

    items = [
        DatasetItem(
            dataset_id=dataset["dataset_id"],
            name=dataset["name"],
            description=dataset.get("description"),
            owner=dataset.get("owner"),
            type=dataset["type"],
        )
        for dataset in filtered[:limit]
    ]

    return DatasetListResponse(
        items=items,
        total=len(items),
        filters={
            "q": q,
            "catalog": catalog,
            "schema": schema,
            "owner": owner,
            "limit": limit,
        },
    )


def get_dataset(dataset_id: str) -> DatasetDetailResponse:
    dataset = find_dataset_by_id(dataset_id)

    if dataset:
        return DatasetDetailResponse(
            dataset_id=dataset["dataset_id"],
            name=dataset["name"],
            catalog=dataset.get("catalog"),
            schema=dataset.get("schema"),
            table=dataset.get("table"),
            type=dataset["type"],
            description=dataset.get("description"),
            owner=dataset.get("owner"),
            columns=[
                DatasetColumn(
                    name=column["name"],
                    data_type=column.get("data_type"),
                    nullable=column.get("nullable"),
                    description=column.get("description"),
                )
                for column in dataset.get("columns", [])
            ],
            documentation=[
                DatasetDocument(
                    document_id=document["document_id"],
                    title=document["title"],
                )
                for document in dataset.get("documentation", [])
            ],
        )

    return DatasetDetailResponse(
        dataset_id=dataset_id,
        name=dataset_id,
        catalog=None,
        schema=None,
        table=None,
        type="table",
        description=None,
        owner=None,
        columns=[],
        documentation=[],
    )
