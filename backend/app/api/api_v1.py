from fastapi import APIRouter

api_router = APIRouter()

# Register each module's router here, e.g.:
# from app.modules.health.router import router as health_router
# api_router.include_router(health_router, tags=["Health"])
