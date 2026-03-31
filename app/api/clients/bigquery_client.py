from typing import Any, Dict, List

from google.cloud import bigquery

from app.api.core.config import settings


class BigQueryClient:
    def __init__(self) -> None:
        self.project_id = settings.bigquery_project_id
        self.client = bigquery.Client(project=self.project_id)

    def query(self, sql: str) -> List[Dict[str, Any]]:
        rows = self.client.query(sql).result()
        return [dict(row.items()) for row in rows]
