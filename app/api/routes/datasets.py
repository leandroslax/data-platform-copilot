from typing import Optional

from fastapi import APIRouter, Query

from app.api.schemas.datasets import DatasetDetailResponse, DatasetListResponse
from app.api.services.dataset_service import get_dataset, list_datasets

router = APIRouter()


@router.get("/datasets", response_model=DatasetListResponse)
def datasets(
    q: Optional[str] = Query(default=None),
    catalog: Optional[str] = Query(default=None),
    schema: Optional[str] = Query(default=None),
    owner: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
) -> DatasetListResponse:
    return list_datasets(q=q, catalog=catalog, schema=schema, owner=owner, limit=limit)


@router.get("/datasets/{dataset_id}", response_model=DatasetDetailResponse)
def dataset_detail(dataset_id: str) -> DatasetDetailResponse:
    return get_dataset(dataset_id)
