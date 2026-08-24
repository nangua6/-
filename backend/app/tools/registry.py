from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.base import BaseTool, ToolContext, ToolResult
from app.tools.product_tools import GetProductTool
from app.tools.inventory_tools import GetInventoryTool, SearchInventoryTool
from app.tools.order_tools import GetOrderTool, GetProductionStatusTool, GetPurchaseOrderTool, GetCustomerTool
from app.tools.order_risk import AnalyzeOrderRiskTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def allowed_tools(self, role: str) -> list[BaseTool]:
        return [tool for tool in self._tools.values() if tool.public or role == "ADMIN"]

    def schema_list(self, role: str) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self.allowed_tools(role)]

    async def run(self, name: str, ctx: ToolContext, arguments: dict[str, Any], db: AsyncSession) -> ToolResult:
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(ok=False, error=f"Tool '{name}' not found")
        if not tool.public and ctx.role != "ADMIN":
            return ToolResult(ok=False, error="Permission denied")
        return await tool.run(ctx, arguments, db)


def default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(GetProductTool())
    registry.register(GetInventoryTool())
    registry.register(SearchInventoryTool())
    registry.register(GetOrderTool())
    registry.register(GetProductionStatusTool())
    registry.register(GetPurchaseOrderTool())
    registry.register(GetCustomerTool())
    registry.register(AnalyzeOrderRiskTool())
    return registry
