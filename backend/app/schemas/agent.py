from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=8000)
    model: str | None = None


class AgentResponse(BaseModel):
    answer: str
    trace_id: str
    tools_called: list[str]
    model: str
    input_tokens: int
    output_tokens: int
    citations: list[dict[str, Any]] = []
