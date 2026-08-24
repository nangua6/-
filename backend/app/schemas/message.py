from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str
    content: str = ""
    metadata: dict[str, Any] = {}


class MessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
