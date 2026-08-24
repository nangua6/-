from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str = "New Session"


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
