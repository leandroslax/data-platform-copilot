from typing import Optional

from app.api.schemas.datasets import DatasetDetailResponse, DatasetListResponse


def list_datasets(
    q: Optional[str],
    catalog: Optional[str],
    schema: Optional[str],
    owner: Optional[str],
    limit: int,
) -> DatasetListResponse:
    return DatasetListResponse(
        items=[],
        total=0,
        filters={
            "q": q,
            "catalog": catalog,
            "schema": schema,
            "owner": owner,
            "limit": limit,
        },
    )


def get_dataset(dataset_id: str) -> DatasetDetailResponse:
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
