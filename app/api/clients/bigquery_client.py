from typing import Any, Dict, List, Optional

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from app.api.core.config import settings


class BigQueryClient:
    def __init__(self) -> None:
        self.project_id = settings.bigquery_project_id
        self._client: bigquery.Client | None = None

    @property
    def client(self) -> bigquery.Client:
        if self._client is None:
            self._client = bigquery.Client(project=self.project_id)
        return self._client

    def query(self, sql: str) -> List[Dict[str, Any]]:
        rows = self.client.query(sql).result()
        return [dict(row.items()) for row in rows]

    def get_table(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        parts = dataset_id.split(".")
        if len(parts) == 3:
            project_id, dataset_name, table_name = parts
        elif len(parts) == 2:
            project_id = self.project_id
            dataset_name, table_name = parts
        else:
            return None

        table_ref = f"{project_id}.{dataset_name}.{table_name}"

        try:
            table = self.client.get_table(table_ref)
        except NotFound:
            return None

        return {
            "dataset_id": table_ref,
            "name": table_ref,
            "catalog": project_id,
            "schema": dataset_name,
            "table": table_name,
            "type": "table",
            "description": table.description,
            "owner": None,
            "columns": [
                {
                    "name": column.name,
                    "data_type": column.field_type,
                    "nullable": column.is_nullable,
                    "description": column.description,
                }
                for column in table.schema
            ],
            "documentation": [],
        }

    def list_tables(self, dataset_name: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        resolved_project_id = project_id or self.project_id
        dataset_ref = f"{resolved_project_id}.{dataset_name}"

        try:
            table_items = list(self.client.list_tables(dataset_ref))
        except NotFound:
            return []

        tables: List[Dict[str, Any]] = []
        for table_item in table_items:
            table = self.get_table(f"{resolved_project_id}.{dataset_name}.{table_item.table_id}")
            if table:
                tables.append(table)

        return tables
