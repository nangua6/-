from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_payload
from app.models.session import ConversationSession
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/api/sessions/{session_id}/messages", tags=["messages"])


async def _owned_session(session_id: str, user_id: str, db: AsyncSession) -> ConversationSession:
    session = await db.get(ConversationSession, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("", response_model=List[MessageOut])
async def list_messages(session_id: str, payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    await _owned_session(session_id, payload["sub"], db)
    rows = (await db.execute(select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc()))).scalars().all()
    out = []
    for row in rows:
        out.append(
            MessageOut(
                id=row.id,
                session_id=row.session_id,
                role=row.role,
                content=row.content,
                metadata=row.metadata_ or {},
                created_at=row.created_at,
            )
        )
    return out


@router.post("", response_model=MessageOut)
async def create_message(session_id: str, body: MessageCreate, payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    await _owned_session(session_id, payload["sub"], db)
    message = Message(session_id=session_id, role=body.role, content=body.content, metadata_=body.metadata)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return MessageOut(
        id=message.id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        metadata=message.metadata_ or {},
        created_at=message.created_at,
    )
