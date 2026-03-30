import json
from typing import Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.api.core.config import settings


class DatabricksClient:
    def __init__(self) -> None:
        self.host = settings.databricks_host.rstrip("/")
        self.token = settings.databricks_token
        self.catalog = settings.databricks_catalog

    def is_configured(self) -> bool:
        return bool(self.host and self.token)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict:
        if not self.is_configured():
            return {}

        query = f"?{urlencode(params)}" if params else ""
        request = Request(
            f"{self.host}{path}{query}",
            headers=self._get_headers(),
            method="GET",
        )

        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_tables(self) -> List[Dict]:
        if not self.is_configured():
            return []

        response = self._get(
            "/api/2.1/unity-catalog/tables",
            params={"catalog_name": self.catalog},
        )

        tables = response.get("tables", [])
        normalized_tables: List[Dict] = []

        for table in tables:
            full_name = table.get("full_name") or ""
            catalog = table.get("catalog_name") or self.catalog
            schema_name = table.get("schema_name")
            table_name = table.get("name")

            if not full_name and catalog and schema_name and table_name:
                full_name = f"{catalog}.{schema_name}.{table_name}"

            normalized_tables.append(
                {
                    "dataset_id": full_name,
                    "name": full_name,
                    "catalog": catalog,
                    "schema": schema_name,
                    "table": table_name,
                    "type": (table.get("table_type") or "table").lower(),
                    "description": table.get("comment"),
                    "owner": table.get("owner"),
                    "columns": [],
                    "documentation": [],
                }
            )

        return normalized_tables

    def get_jobs(self) -> List[Dict]:
        if not self.is_configured():
            return []

        response = self._get("/api/2.1/jobs/list")
        jobs = response.get("jobs", [])
        normalized_jobs: List[Dict] = []

        for job in jobs:
            settings_payload = job.get("settings", {})
            normalized_jobs.append(
                {
                    "job_id": str(job.get("job_id", "")),
                    "job_name": settings_payload.get("name") or str(job.get("job_id", "")),
                    "status": "active",
                }
            )

        return normalized_jobs

    def get_job_runs(self) -> List[Dict]:
        if not self.is_configured():
            return []

        response = self._get("/api/2.1/jobs/runs/list", params={"limit": "25"})
        runs = response.get("runs", [])
        normalized_runs: List[Dict] = []

        for run in runs:
            state = run.get("state", {})
            normalized_runs.append(
                {
                    "run_id": str(run.get("run_id", "")),
                    "job_id": str(run.get("job_id", "")),
                    "lifecycle_state": state.get("life_cycle_state"),
                    "result_state": state.get("result_state"),
                    "state_message": state.get("state_message"),
                    "start_time": str(run.get("start_time", "")),
                    "end_time": str(run.get("end_time", "")),
                }
            )

        return normalized_runs

    def get_lineage(self) -> List[Dict]:
        if not self.is_configured():
            return []

        return []
