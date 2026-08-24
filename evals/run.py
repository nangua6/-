from __future__ import annotations

import asyncio
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.db.session import build_engine, build_session_factory
from app.ai.mock_provider import MockModelProvider
from app.agents.agent_service import AgentService
from app.rag.retriever import build_retriever
from app.services.agent_runner import load_agent_system_prompt
from app.tools.base import ToolContext
from app.tools.registry import default_tool_registry

DATASET_PATH = Path(__file__).resolve().parent / "dataset.jsonl"
RESULT_DIR = Path(__file__).resolve().parents[1] / "eval_results"


def load_dataset() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


async def run_eval() -> dict[str, Any]:
    settings = get_settings()
    engine = build_engine(settings, use_pool=False)
    factory = build_session_factory(engine)

    dataset = load_dataset()
    total = len(dataset)
    tool_ok = 0
    argument_ok = 0
    rag_ok = 0
    success_ok = 0
    details: list[dict[str, Any]] = []

    async with factory() as db:
        agent = AgentService(provider=MockModelProvider(), tool_registry=default_tool_registry(), retriever=build_retriever())
        for item in dataset:
            result = await agent.run(
                user_message=item["question"],
                history=[],
                system_prompt=load_agent_system_prompt(),
                db=db,
                ctx=ToolContext(role="ADMIN"),
            )

            expected_tool = item.get("expected_tool")
            tool_hit = expected_tool in result.tools_called if expected_tool else False
            if tool_hit:
                tool_ok += 1

            keyword_hit = any(keyword in result.answer for keyword in item.get("expected_keywords", []))
            if keyword_hit:
                rag_ok += 1

            citation_hit = bool(result.retrieval_results) if item.get("expected_citation") else False
            if citation_hit:
                argument_ok += 1

            task_hit = bool(result.answer)
            if task_hit:
                success_ok += 1

            details.append({
                "id": item.get("id"),
                "type": item.get("type"),
                "question": item.get("question"),
                "expected_tool": expected_tool,
                "tools_called": result.tools_called,
                "tool_hit": tool_hit,
                "citation_hit": citation_hit,
                "keyword_hit": keyword_hit,
                "task_hit": task_hit,
                "trace_id": result.trace_id,
            })

    await engine.dispose()

    summary = {
        "run_time": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "tool_accuracy": round(tool_ok / total * 100, 2),
        "argument_accuracy": round(argument_ok / total * 100, 2),
        "retrieval_recall": round(rag_ok / total * 100, 2),
        "task_success_rate": round(success_ok / total * 100, 2),
        "notes": "Mock evaluation for local validation; replace with live model evaluation later.",
    }

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = RESULT_DIR / f"eval_{ts}.json"
    csv_path = RESULT_DIR / f"eval_{ts}.csv"

    json_path.write_text(json.dumps({"summary": summary, "details": details}, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(details[0].keys()))
        writer.writeheader()
        writer.writerows(details)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")
    return summary


if __name__ == "__main__":
    asyncio.run(run_eval())
