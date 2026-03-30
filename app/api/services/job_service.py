from typing import Optional

from app.api.schemas.jobs import JobIncident, JobIncidentsResponse, JobItem, JobListResponse
from app.api.services.mock_data import JOBS


def list_jobs(q: Optional[str], status: Optional[str], limit: int) -> JobListResponse:
    filtered = JOBS

    if q:
        query = q.lower()
        filtered = [
            job
            for job in filtered
            if query in job["job_name"].lower() or query in job["job_id"].lower()
        ]

    if status:
        filtered = [
            job for job in filtered if (job.get("status") or "").lower() == status.lower()
        ]

    items = [
        JobItem(
            job_id=job["job_id"],
            job_name=job["job_name"],
            status=job.get("status"),
        )
        for job in filtered[:limit]
    ]

    return JobListResponse(
        items=items,
        total=len(items),
        filters={
            "q": q,
            "status": status,
            "limit": limit,
        },
    )


def get_job_incidents(job_id: str) -> JobIncidentsResponse:
    for job in JOBS:
        if job["job_id"] == job_id:
            return JobIncidentsResponse(
                job_id=job["job_id"],
                job_name=job["job_name"],
                latest_status=job.get("latest_status"),
                latest_error_summary=job.get("latest_error_summary"),
                recent_incidents=[
                    JobIncident(
                        run_id=incident["run_id"],
                        severity=incident["severity"],
                        event_type=incident["event_type"],
                        event_timestamp=incident["event_timestamp"],
                        summary=incident["summary"],
                    )
                    for incident in job.get("recent_incidents", [])
                ],
            )

    return JobIncidentsResponse(
        job_id=job_id,
        job_name=None,
        latest_status=None,
        latest_error_summary=None,
        recent_incidents=[],
    )
