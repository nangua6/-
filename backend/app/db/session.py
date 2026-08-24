from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
import redis.asyncio as aioredis

from app.core.config import Settings


def build_engine(settings: Settings, *, use_pool: bool = True):
    return create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
        poolclass=None if use_pool else NullPool,
    )


def build_session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def build_redis(settings: Settings):
    return aioredis.from_url(settings.redis_url, decode_responses=True)
