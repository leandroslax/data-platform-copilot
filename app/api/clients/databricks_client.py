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

        return []

    def get_job_runs(self) -> List[Dict]:
        if not self.is_configured():
            return []

        return []

    def get_lineage(self) -> List[Dict]:
        if not self.is_configured():
            return []

        return []
