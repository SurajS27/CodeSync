from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import log_startup, log_shutdown, setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.api.router import api_router

# Setup logging configuration immediately at startup
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup logic
    log_startup()
    yield
    # Application shutdown logic
    log_shutdown()


app = FastAPI(
    title="CodeSync API",
    description="Backend API for automatically synchronizing accepted coding challenge submissions to GitHub",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
# In production, restrict this to specific origins (like the Chrome Extension ID)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Register central routers
app.include_router(api_router, prefix="/api")
