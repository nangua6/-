from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Product
from app.tools.base import BaseTool, ToolContext, ToolResult


class GetProductTool(BaseTool):
    name = "get_product"
    description = "根据产品编码查询产品信息"

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "product_code": {"type": "string", "description": "产品编码，例如 A001"},
                },
                "required": ["product_code"],
            },
        }

    async def run(self, ctx: ToolContext, arguments: dict[str, Any], db: AsyncSession) -> ToolResult:
        code = arguments.get("product_code")
        if not code:
            return ToolResult(ok=False, error="product_code is required")
        product = (await db.execute(select(Product).where(Product.product_code == code))).scalar_one_or_none()
        if not product:
            return ToolResult(ok=False, error="Product not found")
        return ToolResult(ok=True, data={
            "product_code": product.product_code,
            "product_name": product.product_name,
            "category": product.category,
            "unit": product.unit,
        })
