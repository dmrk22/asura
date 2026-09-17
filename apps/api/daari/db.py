"""Async SQLAlchemy engine + sessionmaker, built from Settings.DATABASE_URL."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from daari.config import settings


def _to_asyncpg_url(url: str) -> str:
    """`postgresql://` -> `postgresql+asyncpg://`; leaves an already-correct URL alone."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


engine = create_async_engine(_to_asyncpg_url(settings.DATABASE_URL), pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
