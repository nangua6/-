from __future__ import annotations

from typing import AsyncIterator

import redis.asyncio as aioredis
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.session import build_engine, build_session_factory, build_redis

_state: dict = {}


def _get_state(settings: Settings):
    key = (settings.database_url, settings.redis_url)
    if key not in _state:
        engine = build_engine(settings)
        _state[key] = {
            "engine": engine,
            "session_factory": build_session_factory(engine),
            "redis": build_redis(settings),
        }
    return _state[key]


async def get_db(settings: Settings = Depends(get_settings)) -> AsyncIterator[AsyncSession]:
    state = _get_state(settings)
    async with state["session_factory"]() as session:
        yield session


async def get_redis(settings: Settings = Depends(get_settings)) -> aioredis.Redis:
    state = _get_state(settings)
    return state["redis"]


async def get_current_user_payload(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return payload


async def require_admin(payload: dict = Depends(get_current_user_payload)) -> dict:
    if payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return payload
