from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1 import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

API_PREFIX = "/api/v1"
CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
CORS_HEADERS = ["Accept", "Content-Type"]


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
    # Only the listed origins (the web app) may call the API from a browser,
    # with its session cookie. With credentials, methods and headers are
    # listed, never "*" (FastAPI docs → CORS).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
    )
    app.include_router(api_router, prefix=API_PREFIX)
    return app


app = create_app()
