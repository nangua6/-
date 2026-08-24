from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ToolContext(BaseModel):
    user_id: str | None = None
    role: str = "USER"


class ToolResult(BaseModel):
    ok: bool
    data: dict[str, Any] = {}
    error: str | None = None


class BaseTool:
    name: str = ""
    description: str = ""
    public: bool = True

    def schema(self) -> dict[str, Any]:
        raise NotImplementedError

    async def run(self, ctx: ToolContext, arguments: dict[str, Any]) -> ToolResult:
        raise NotImplementedError
