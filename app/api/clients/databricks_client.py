import json
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
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

        try:
            schemas_response = self._get(
                "/api/2.1/unity-catalog/schemas",
                params={"catalog_name": self.catalog},
            )
        except (HTTPError, URLError):
            return []

        schemas = schemas_response.get("schemas", [])
        normalized_tables: List[Dict] = []

        for schema in schemas:
            schema_name = schema.get("name")
            if not schema_name or schema_name == "information_schema":
                continue

            try:
                tables_response = self._get(
                    "/api/2.1/unity-catalog/tables",
                    params={
                        "catalog_name": self.catalog,
                        "schema_name": schema_name,
                    },
                )
            except (HTTPError, URLError):
                continue

            for table in tables_response.get("tables", []):
                normalized_tables.append(self._normalize_table(table, schema_name))

        return normalized_tables

    def get_table(self, dataset_id: str) -> Optional[Dict]:
        if not self.is_configured():
            return None

        parts = dataset_id.split(".")
        if len(parts) != 3:
            return None

        catalog_name, schema_name, table_name = parts

        try:
            response = self._get(
                f"/api/2.1/unity-catalog/tables/{catalog_name}.{schema_name}.{table_name}"
            )
        except (HTTPError, URLError):
            return None

        if not response:
            return None

        return self._normalize_table(response, schema_name)

    def _normalize_table(self, table: Dict, fallback_schema_name: Optional[str] = None) -> Dict:
        full_name = table.get("full_name") or ""
        catalog = table.get("catalog_name") or self.catalog
        schema_name = table.get("schema_name") or fallback_schema_name
        table_name = table.get("name")

        if not full_name and catalog and schema_name and table_name:
            full_name = f"{catalog}.{schema_name}.{table_name}"

        columns = []
        for column in table.get("columns", []):
            columns.append(
                {
                    "name": column.get("name"),
                    "data_type": column.get("type_text") or column.get("type_name"),
                    "nullable": column.get("type_json") is not None,
                    "description": column.get("comment"),
                }
            )

        return {
            "dataset_id": full_name,
            "name": full_name,
            "catalog": catalog,
            "schema": schema_name,
            "table": table_name,
            "type": (table.get("table_type") or "table").lower(),
            "description": table.get("comment"),
            "owner": table.get("owner"),
            "columns": columns,
            "documentation": [],
        }

    def get_jobs(self) -> List[Dict]:
        if not self.is_configured():
            return []

        try:
            response = self._get("/api/2.1/jobs/list")
        except (HTTPError, URLError):
            return []

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

        try:
            response = self._get("/api/2.1/jobs/runs/list", params={"limit": "25"})
        except (HTTPError, URLError):
            return []

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
