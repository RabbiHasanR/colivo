from fastapi import FastAPI

from app.api.api_v1 import api_router
from app.core.config import settings

API_PREFIX = "/api/v1"

app = FastAPI(
    title=settings.project_name,
    description="Colivo REST API: meals, groceries, rent and bills for shared homes.",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.include_router(api_router, prefix=API_PREFIX)
