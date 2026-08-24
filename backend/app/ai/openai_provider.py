from __future__ import annotations

import json
from typing import Any

import httpx

from app.ai.provider import ChatMessage, ChatResult, ToolCall, ModelProvider


class OpenAICompatibleProvider(ModelProvider):
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> ChatResult:
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": tool,
                }
                for tool in tools
            ]

        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        message = choice["message"]
        usage = data.get("usage", {})

        tool_calls: list[ToolCall] = []
        for call in message.get("tool_calls") or []:
            fn = call["function"]
            tool_calls.append(
                ToolCall(
                    id=call["id"],
                    name=fn["name"],
                    arguments=json.loads(fn["arguments"]) if isinstance(fn["arguments"], str) else fn["arguments"],
                )
            )

        return ChatResult(
            content=message.get("content") or "",
            tool_calls=tool_calls,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            model=data.get("model", model or self.model),
        )
