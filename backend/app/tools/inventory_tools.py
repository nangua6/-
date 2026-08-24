from __future__ import annotations

from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Product, Inventory
from app.tools.base import BaseTool, ToolContext, ToolResult


class GetInventoryTool(BaseTool):
    name = "get_inventory"
    description = "根据产品编码查询库存汇总"

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "product_code": {"type": "string"},
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
        total = (await db.execute(select(func.coalesce(func.sum(Inventory.quantity), 0)).where(Inventory.product_id == product.id))).scalar_one()
        return ToolResult(ok=True, data={"product_code": product.product_code, "quantity": int(total)})


class SearchInventoryTool(BaseTool):
    name = "search_inventory"
    description = "按关键词检索库存相关产品"

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                },
                "required": ["keyword"],
            },
        }

    async def run(self, ctx: ToolContext, arguments: dict[str, Any], db: AsyncSession) -> ToolResult:
        keyword = arguments.get("keyword")
        if not keyword:
            return ToolResult(ok=False, error="keyword is required")
        stmt = (
            select(Product.product_code, Product.product_name, func.coalesce(func.sum(Inventory.quantity), 0).label("quantity"))
            .join(Inventory, Inventory.product_id == Product.id, isouter=True)
            .where(Product.product_name.ilike(f"%{keyword}%") | Product.product_code.ilike(f"%{keyword}%"))
            .group_by(Product.id)
            .limit(10)
        )
        rows = (await db.execute(stmt)).all()
        return ToolResult(ok=True, data={"items": [{"product_code": r[0], "product_name": r[1], "quantity": int(r[2])} for r in rows]})
