from __future__ import annotations

from pathlib import Path

from app.agents.agent_service import AgentService
from app.ai.provider import ModelProvider
from app.rag.retriever import Retriever, build_retriever
from app.tools.registry import ToolRegistry, default_tool_registry

_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "agent_system.txt"


def build_agent_service(provider: ModelProvider) -> AgentService:
    registry = default_tool_registry()
    retriever = build_retriever()
    return AgentService(provider=provider, tool_registry=registry, retriever=retriever)


def load_agent_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")
