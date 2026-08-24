from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.memory.context import compress_history


async def load_session_history(db: AsyncSession, session_id: str, max_messages: int = 20) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = (await db.execute(select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc()))).scalars().all()
    history = [{"role": r.role, "content": r.content, "metadata": r.metadata_ or {}} for r in rows]
    return compress_history(history, max_messages=max_messages)
