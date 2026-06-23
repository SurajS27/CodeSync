from fastapi import APIRouter
from app.api.v1 import health

api_router = APIRouter()

# Register sub-routers under version 1 prefix
api_router.include_router(health.router, tags=["health"])
