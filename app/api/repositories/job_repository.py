from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.api.clients.databricks_client import DatabricksClient
from app.api.services.mock_data import JOBS


def _normalize_job_record(job: Dict[str, Any], job_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    job_id = str(job.get("job_id") or job.get("id") or "")
    job_name = job.get("job_name") or job.get("name") or job_id
    status = job.get("status")

    if status is None and "active" in job:
        status = "active" if job.get("active") else "inactive"

    incidents = [_normalize_job_run(job_run) for job_run in job_runs if str(job_run.get("job_id")) == job_id]
    latest_incident = incidents[0] if incidents else None

    normalized = deepcopy(job)
    normalized["job_id"] = job_id
    normalized["job_name"] = job_name
    normalized["status"] = status
    normalized["latest_status"] = (
        job.get("latest_status")
        or (latest_incident.get("derived_status") if latest_incident else None)
    )
    normalized["latest_error_summary"] = (
        job.get("latest_error_summary")
        or (latest_incident.get("summary") if latest_incident else None)
    )
    normalized["recent_incidents"] = [
        {
            "run_id": incident["run_id"],
            "severity": incident["severity"],
            "event_type": incident["event_type"],
            "event_timestamp": incident["event_timestamp"],
            "summary": incident["summary"],
        }
        for incident in incidents
    ]

    return normalized


def _normalize_job_run(job_run: Dict[str, Any]) -> Dict[str, Any]:
    run_id = str(job_run.get("run_id") or job_run.get("id") or "")
    result_state = (job_run.get("result_state") or job_run.get("status_classification") or "").lower()
    lifecycle_state = (job_run.get("lifecycle_state") or "").lower()
    event_timestamp = str(
        job_run.get("event_timestamp")
        or job_run.get("end_time")
        or job_run.get("start_time")
        or ""
    )
    summary = (
        job_run.get("summary")
        or job_run.get("error_message")
        or job_run.get("state_message")
        or "No summary available"
    )

    if result_state in {"failed", "error", "timedout", "timeout"}:
        severity = "high"
        event_type = "job_failure"
        derived_status = "failed"
    elif result_state in {"success", "succeeded"}:
        severity = "low"
        event_type = "job_success"
        derived_status = "success"
    elif lifecycle_state in {"running", "pending"}:
        severity = "medium"
        event_type = "job_in_progress"
        derived_status = lifecycle_state
    else:
        severity = "medium"
        event_type = "job_event"
        derived_status = result_state or lifecycle_state or "unknown"

    return {
        "run_id": run_id,
        "severity": severity,
        "event_type": event_type,
        "event_timestamp": event_timestamp,
        "summary": summary,
        "derived_status": derived_status,
    }


def _get_job_source() -> List[Dict[str, Any]]:
    client = DatabricksClient()

    if client.is_configured():
        jobs = client.get_jobs()
        job_runs = client.get_job_runs()

        if jobs:
            return [_normalize_job_record(job, job_runs) for job in jobs]

    return [deepcopy(job) for job in JOBS]


def list_jobs() -> List[Dict[str, Any]]:
    return _get_job_source()


def find_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    for job in _get_job_source():
        if job["job_id"] == job_id:
            return job
    return None
