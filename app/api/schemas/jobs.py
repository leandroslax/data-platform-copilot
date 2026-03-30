from typing import List, Optional

from pydantic import BaseModel


class JobItem(BaseModel):
    job_id: str
    job_name: str
    status: Optional[str] = None


class JobListResponse(BaseModel):
    items: List[JobItem]
    total: int
    filters: dict


class JobIncident(BaseModel):
    run_id: str
    severity: str
    event_type: str
    event_timestamp: str
    summary: str


class JobIncidentsResponse(BaseModel):
    job_id: str
    job_name: Optional[str] = None
    latest_status: Optional[str] = None
    latest_error_summary: Optional[str] = None
    recent_incidents: List[JobIncident]
