from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_payload
from app.models.session import ConversationSession
from app.models.message import Message
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent_runner import build_agent_service, load_agent_system_prompt
from app.ai.mock_provider import MockModelProvider
from app.ai.openai_provider import OpenAICompatibleProvider
from app.core.config import get_settings
from app.memory.manager import load_session_history
from app.tools.base import ToolContext

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _provider():
    settings = get_settings()
    if settings.ai_provider == "openai" and settings.ai_api_key:
        return OpenAICompatibleProvider(settings.ai_base_url, settings.ai_api_key, settings.ai_model, settings.request_timeout)
    return MockModelProvider()


@router.post("/completions", response_model=AgentResponse)
async def agent_completions(body: AgentRequest, payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    if body.session_id:
        session = await db.get(ConversationSession, body.session_id)
        if not session or session.user_id != payload["sub"]:
            raise HTTPException(status_code=404, detail="Session not found")

    history: List[dict[str, str]] = []
    memory_summary: dict[str, object] = {}
    if body.session_id:
        history, memory_summary = await load_session_history(db, body.session_id, max_messages=get_settings().max_context_messages)

    provider = _provider()
    agent = build_agent_service(provider)
    result = await agent.run(
        user_message=body.message,
        history=history,
        system_prompt=load_agent_system_prompt(),
        db=db,
        ctx=ToolContext(user_id=payload["sub"], role=payload.get("role", "USER")),
        session_id=body.session_id,
        model=body.model,
    )

    if body.session_id:
        db.add(Message(session_id=body.session_id, role="user", content=body.message))
        db.add(Message(session_id=body.session_id, role="assistant", content=result.answer, metadata_={
            "trace_id": result.trace_id,
            "tools_called": result.tools_called,
            "model": result.model,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "retrieval_count": len(result.retrieval_results),
            "memory_summary": memory_summary,
        }))
        await db.commit()

    citations = []
    for idx, item in enumerate(result.retrieval_results, start=1):
        citations.append({"index": idx, "source_title": item.get("source_title"), "section_title": item.get("section_title"), "page_number": item.get("page_number"), "chunk_id": item.get("chunk_id")})

    return AgentResponse(
        answer=result.answer,
        trace_id=result.trace_id,
        tools_called=result.tools_called,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        citations=citations,
    )
