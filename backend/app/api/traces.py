from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_admin
from app.models.trace import AgentTrace, ToolTrace
from app.models.business import Order, Product

router = APIRouter(prefix="/api", tags=["observability"])


@router.get("/traces")
async def list_traces(page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100), _admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    total = (await db.execute(select(func.count(AgentTrace.id)))).scalar_one()
    rows = (await db.execute(select(AgentTrace).order_by(AgentTrace.start_time.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return {
        "total": total,
        "items": [
            {
                "trace_id": r.trace_id,
                "model": r.model,
                "latency_ms": r.latency_ms,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "estimated_cost": r.estimated_cost,
                "final_status": r.final_status,
                "start_time": r.start_time.isoformat() if r.start_time else None,
            }
            for r in rows
        ],
    }


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str, _admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    trace = (await db.execute(select(AgentTrace).where(AgentTrace.trace_id == trace_id))).scalar_one_or_none()
    if not trace:
        return {}
    tools = (await db.execute(select(ToolTrace).where(ToolTrace.trace_id == trace_id).order_by(ToolTrace.created_at))).scalars().all()
    return {
        "trace_id": trace.trace_id,
        "model": trace.model,
        "latency_ms": trace.latency_ms,
        "input_tokens": trace.input_tokens,
        "output_tokens": trace.output_tokens,
        "estimated_cost": trace.estimated_cost,
        "final_status": trace.final_status,
        "error": trace.error,
        "tools": [
            {
                "tool_name": t.tool_name,
                "success": t.success,
                "latency_ms": t.latency_ms,
                "input": t.input,
                "output": t.output,
            }
            for t in tools
        ],
    }


@router.get("/dashboard")
async def dashboard_metrics(_admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    total_traces = (await db.execute(select(func.count(AgentTrace.id)))).scalar_one()
    success_traces = (await db.execute(select(func.count(AgentTrace.id)).where(AgentTrace.final_status == "success"))).scalar_one()
    avg_latency = (await db.execute(select(func.avg(AgentTrace.latency_ms)))).scalar_one() or 0
    total_tokens = (await db.execute(select(func.coalesce(func.sum(AgentTrace.input_tokens + AgentTrace.output_tokens), 0)))).scalar_one()
    total_cost = (await db.execute(select(func.coalesce(func.sum(AgentTrace.estimated_cost), 0.0)))).scalar_one()
    tool_total = (await db.execute(select(func.count(ToolTrace.id)))).scalar_one()
    tool_success = (await db.execute(select(func.count(ToolTrace.id)).where(ToolTrace.success == True))).scalar_one()  # noqa: E712
    order_count = (await db.execute(select(func.count(Order.id)))).scalar_one()
    product_count = (await db.execute(select(func.count(Product.id)))).scalar_one()
    return {
        "ai_requests": total_traces,
        "task_success_rate": round(success_traces / total_traces, 4) if total_traces else 0,
        "tool_success_rate": round(tool_success / tool_total, 4) if tool_total else 0,
        "average_latency_ms": round(float(avg_latency), 2),
        "total_tokens": total_tokens,
        "estimated_cost": round(float(total_cost), 4),
        "orders": order_count,
        "products": product_count,
    }
