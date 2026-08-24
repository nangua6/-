from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_payload
from app.models.session import ConversationSession
from app.schemas.session import SessionCreate, SessionOut

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=List[SessionOut])
async def list_sessions(payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(ConversationSession).where(ConversationSession.user_id == payload["sub"]).order_by(ConversationSession.updated_at.desc()))).scalars().all()
    return rows


@router.post("", response_model=SessionOut)
async def create_session(body: SessionCreate, payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    session = ConversationSession(user_id=payload["sub"], title=body.title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
