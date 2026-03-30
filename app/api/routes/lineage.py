from fastapi import APIRouter

router = APIRouter()


@router.get("/lineage/{dataset_id}")
def get_lineage(dataset_id: str) -> dict:
    return {
        "dataset_id": dataset_id,
        "upstream": [],
        "downstream": [],
        "related_jobs": [],
    }
