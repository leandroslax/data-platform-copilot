from typing import Optional

from fastapi import APIRouter, Query

from app.api.schemas.jobs import JobIncidentsResponse, JobListResponse
from app.api.services.job_service import get_job_incidents, list_jobs

router = APIRouter()


@router.get("/jobs", response_model=JobListResponse)
def jobs(
    q: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
) -> JobListResponse:
    return list_jobs(q=q, status=status, limit=limit)


@router.get("/jobs/{job_id}/incidents", response_model=JobIncidentsResponse)
def job_incidents(job_id: str) -> JobIncidentsResponse:
    return get_job_incidents(job_id)
