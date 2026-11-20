from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1 import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    """Build the Colivo API app.

    Returns:
        The app, with error handlers and every module router.
    """
    app = FastAPI(
        title=settings.project_name,
        description=(
            "Colivo REST API: meals, groceries, rent and bills for shared homes."
        ),
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )
    register_exception_handlers(app)
    # Only the listed origins (the web app) may call the API from a browser.
    # No credentials: the web sends its token in the Authorization header.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=API_PREFIX)
    return app


app = create_app()
