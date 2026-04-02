from typing import Any, Dict, List, Optional

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from app.api.core.config import settings


class BigQueryClient:
    def __init__(self) -> None:
        self.project_id = settings.bigquery_project_id
        self.client = bigquery.Client(project=self.project_id)

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
