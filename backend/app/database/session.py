from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# Create asynchronous engine targeting psycopg (v3)
# Settings.DATABASE_URL should be in the format: postgresql+psycopg://user:password@host:port/db
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENV == "development",
    future=True,
    pool_pre_ping=True,
    pool_recycle=300
)

# Configure the sessionmaker for AsyncSession
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for yielding an asynchronous database session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
