from fastapi import APIRouter

from app.api.schemas.search import MetadataSyncResponse
from app.api.services.metadata_catalog_service import refresh_metadata_catalog

router = APIRouter()


@router.post("/metadata/sync", response_model=MetadataSyncResponse)
def sync_metadata() -> MetadataSyncResponse:
    return MetadataSyncResponse(**refresh_metadata_catalog())
