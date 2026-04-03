from fastapi import APIRouter, Query

from app.api.schemas.search import SearchResponse, SearchResult
from app.api.services.retrieval_service import search_catalog

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search(q: str = Query(min_length=2), limit: int = Query(default=5, ge=1, le=20)) -> SearchResponse:
    results = search_catalog(q, limit=limit)
    return SearchResponse(
        query=q,
        items=[
            SearchResult(
                dataset_id=item["dataset_id"],
                name=item["name"],
                owner=item.get("owner"),
                description=item.get("description"),
                source_system=item.get("source_system"),
                score=item["score"],
            )
            for item in results
        ],
        total=len(results),
    )
