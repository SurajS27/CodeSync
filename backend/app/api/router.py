from fastapi import APIRouter

from app.api.v1 import auth, health, repositories, sync

api_router = APIRouter()

# Register sub-routers under version 1 prefix
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    repositories.router, prefix="/repositories", tags=["repositories"]
)
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
