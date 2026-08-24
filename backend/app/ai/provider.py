from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ChatResult:
    content: str
    tool_calls: list[ToolCall]
    input_tokens: int
    output_tokens: int
    model: str


class ModelProvider:
    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> ChatResult:
        raise NotImplementedError
