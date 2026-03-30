from typing import Dict, List

from app.api.core.config import settings


class DatabricksClient:
    def __init__(self) -> None:
        self.host = settings.databricks_host
        self.token = settings.databricks_token
        self.catalog = settings.databricks_catalog

    def is_configured(self) -> bool:
        return bool(self.host and self.token)

    def get_tables(self) -> List[Dict]:
        if not self.is_configured():
            return []

        return []

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
