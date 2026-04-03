import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Data Platform Copilot API"
    app_version: str = "0.1.0"
    app_env: str = os.getenv("APP_ENV", "dev")
    databricks_host: str = os.getenv("DATABRICKS_HOST", "")
    databricks_token: str = os.getenv("DATABRICKS_TOKEN", "")
    databricks_catalog: str = os.getenv("DATABRICKS_CATALOG", "main")
    bigquery_project_id: str = os.getenv("BIGQUERY_PROJECT_ID", "data-platform-copilot-dev")
    novadrive_silver_dataset: str = os.getenv("NOVADRIVE_SILVER_DATASET", "silver_novadrive")
    novadrive_gold_dataset: str = os.getenv("NOVADRIVE_GOLD_DATASET", "gold_novadrive")
    novadrive_metrics_ttl_seconds: int = int(os.getenv("NOVADRIVE_METRICS_TTL_SECONDS", "300"))


settings = Settings()
