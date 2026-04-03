from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.core.config import settings
from app.api.routes.chat import router as chat_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.lineage import router as lineage_router
from app.api.routes.novadrive import router as novadrive_router
from app.api.services.observability_service import refresh_observability_metrics_if_needed

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for metadata discovery, lineage lookup, troubleshooting, and GenAI workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(datasets_router, prefix="/api/v1", tags=["datasets"])
app.include_router(lineage_router, prefix="/api/v1", tags=["lineage"])
app.include_router(jobs_router, prefix="/api/v1", tags=["jobs"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(novadrive_router, prefix="/api/v1", tags=["novadrive"])


@app.middleware("http")
async def refresh_metrics_before_scrape(request: Request, call_next):
    if request.url.path == "/metrics":
        refresh_observability_metrics_if_needed()
    return await call_next(request)

Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics"],
).instrument(app).expose(app, include_in_schema=False)
