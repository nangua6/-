from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Settings


def build_engine(settings: Settings):
    url = settings.database_url
    if url.startswith("sqlite"):
        return create_async_engine(
            url,
            echo=settings.database_echo,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_async_engine(url, echo=settings.database_echo, pool_pre_ping=True)


def build_session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
