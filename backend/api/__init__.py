from fastapi import APIRouter
from api.ask import router as ask_router

api_router = APIRouter(prefix="/api", tags=["api"])

api_router.include_router(ask_router)