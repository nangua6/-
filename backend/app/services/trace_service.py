from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trace import AgentTrace, ToolTrace


async def create_agent_trace(
    db: AsyncSession,
    *,
    trace_id: str,
    session_id: str | None,
    user_id: str | None,
    prompt_version: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    estimated_cost: float,
    latency_ms: float,
    final_status: str,
    error: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AgentTrace:
    trace = AgentTrace(
        trace_id=trace_id,
        session_id=session_id,
        user_id=user_id,
        prompt_version=prompt_version,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost=estimated_cost,
        latency_ms=latency_ms,
        final_status=final_status,
        error=error,
        metadata_=metadata or {},
        end_time=datetime.now(timezone.utc),
    )
    db.add(trace)
    await db.flush()
    return trace


async def create_tool_trace(
    db: AsyncSession,
    *,
    trace_id: str,
    tool_name: str,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
    latency_ms: float,
    success: bool,
    error: str | None = None,
) -> ToolTrace:
    trace = ToolTrace(
        trace_id=trace_id,
        tool_name=tool_name,
        input=input_data,
        output=output_data,
        latency_ms=latency_ms,
        success=success,
        error=error,
    )
    db.add(trace)
    await db.flush()
    return trace
