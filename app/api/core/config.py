from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Data Platform Copilot API"
    app_version: str = "0.1.0"
    app_env: str = "dev"


settings = Settings()
