from typing import Optional

from app.api.schemas.jobs import JobIncidentsResponse, JobListResponse


def list_jobs(q: Optional[str], status: Optional[str], limit: int) -> JobListResponse:
    return JobListResponse(
        items=[],
        total=0,
        filters={
            "q": q,
            "status": status,
            "limit": limit,
        },
    )


def get_job_incidents(job_id: str) -> JobIncidentsResponse:
    return JobIncidentsResponse(
        job_id=job_id,
        job_name=None,
        latest_status=None,
        latest_error_summary=None,
        recent_incidents=[],
    )
