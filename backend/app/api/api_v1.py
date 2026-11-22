from fastapi import APIRouter

from app.modules.accounts.router import router as accounts_router
from app.modules.health.router import router as health_router
from app.modules.homes.router import router as homes_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(accounts_router, tags=["Accounts"])
api_router.include_router(homes_router, tags=["Homes"])
