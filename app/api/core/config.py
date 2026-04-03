import os
from pathlib import Path

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
    metadata_catalog_path: str = os.getenv(
        "METADATA_CATALOG_PATH",
        str(Path("pipelines/metadata/state/catalog_snapshot.json")),
    )
    metadata_embedding_index_path: str = os.getenv(
        "METADATA_EMBEDDING_INDEX_PATH",
        str(Path("pipelines/metadata/state/catalog_embeddings.json")),
    )
    metadata_owner_default: str = os.getenv("METADATA_OWNER_DEFAULT", "data-platform")
    retrieval_result_limit: int = int(os.getenv("RETRIEVAL_RESULT_LIMIT", "5"))
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_response_model: str = os.getenv("OPENAI_RESPONSE_MODEL", "")


settings = Settings()
