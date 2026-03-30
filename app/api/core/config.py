import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Data Platform Copilot API"
    app_version: str = "0.1.0"
    app_env: str = os.getenv("APP_ENV", "dev")
    databricks_host: str = os.getenv("DATABRICKS_HOST", "")
    databricks_token: str = os.getenv("DATABRICKS_TOKEN", "")
    databricks_catalog: str = os.getenv("DATABRICKS_CATALOG", "main")


settings = Settings()
