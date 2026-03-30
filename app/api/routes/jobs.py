from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/jobs")
def list_jobs(
    q: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
) -> dict:
    return {
        "items": [],
        "total": 0,
        "filters": {
            "q": q,
            "status": status,
            "limit": limit,
        },
    }


@router.get("/jobs/{job_id}/incidents")
def get_job_incidents(job_id: str) -> dict:
    return {
        "job_id": job_id,
        "job_name": None,
        "latest_status": None,
        "latest_error_summary": None,
        "recent_incidents": [],
    }
