from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.lineage import router as lineage_router

app = FastAPI(
    title="Data Platform Copilot API",
    version="0.1.0",
    description="API for metadata discovery, lineage lookup, troubleshooting, and GenAI workflows.",
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(datasets_router, prefix="/api/v1", tags=["datasets"])
app.include_router(lineage_router, prefix="/api/v1", tags=["lineage"])
app.include_router(jobs_router, prefix="/api/v1", tags=["jobs"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
