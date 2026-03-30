from typing import Any, Dict, List, Optional

from app.api.services.mock_data import JOBS


def list_jobs() -> List[Dict[str, Any]]:
    return JOBS


def find_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    for job in JOBS:
        if job["job_id"] == job_id:
            return job
    return None
