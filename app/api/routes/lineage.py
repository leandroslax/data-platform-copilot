from fastapi import APIRouter

from app.api.schemas.lineage import LineageResponse
from app.api.services.lineage_service import get_lineage

router = APIRouter()


@router.get("/lineage/{dataset_id}", response_model=LineageResponse)
def lineage(dataset_id: str) -> LineageResponse:
    return get_lineage(dataset_id)
