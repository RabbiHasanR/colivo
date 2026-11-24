from fastapi import APIRouter

from app.modules.accounts.router import router as accounts_router
from app.modules.bills.router import router as bills_router
from app.modules.contacts.router import router as contacts_router
from app.modules.files.router import router as files_router
from app.modules.health.router import router as health_router
from app.modules.homes.router import router as homes_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(accounts_router, tags=["Accounts"])
api_router.include_router(homes_router, tags=["Homes"])
api_router.include_router(contacts_router, tags=["Contacts"])
api_router.include_router(bills_router, tags=["Bills"])
api_router.include_router(files_router, tags=["Files"])
