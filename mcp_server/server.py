from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import run_server
from mcp.types import Tool

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.business import Product, Inventory, Order, ProductionOrder

SERVER = Server("manufacturing-agent-platform")


async def _db_session():
    settings = get_settings()
    engine = create_async_engine(settings.database_url.replace("?ssl=disable", ""), pool_pre_ping=True)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, factory


@SERVER.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_inventory",
            description="根据产品编码查询库存汇总",
            inputSchema={
                "type": "object",
                "properties": {"product_code": {"type": "string"}},
                "required": ["product_code"],
            },
        ),
        Tool(
            name="get_order",
            description="根据订单号查询订单详情",
            inputSchema={
                "type": "object",
                "properties": {"order_no": {"type": "string"}},
                "required": ["order_no"],
            },
        ),
        Tool(
            name="get_production_status",
            description="查询订单对应的生产进度",
            inputSchema={
                "type": "object",
                "properties": {"order_no": {"type": "string"}},
                "required": ["order_no"],
            },
        ),
        Tool(
            name="search_knowledge",
            description="检索企业知识库关键词",
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        ),
    ]


@SERVER.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    engine, factory = await _db_session()
    try:
        async with factory() as session:  # type: AsyncSession
            if name == "get_inventory":
                code = arguments.get("product_code")
                product = (await session.execute(select(Product).where(Product.product_code == code))).scalar_one_or_none()
                if not product:
                    return {"ok": False, "error": "Product not found"}
                total = (await session.execute(select(func.coalesce(func.sum(Inventory.quantity), 0)).where(Inventory.product_id == product.id))).scalar_one()
                return {"ok": True, "data": {"product_code": product.product_code, "quantity": int(total)}}

            if name == "get_order":
                order_no = arguments.get("order_no")
                order = (await session.execute(select(Order).where(Order.order_no == order_no))).scalar_one_or_none()
                if not order:
                    return {"ok": False, "error": "Order not found"}
                return {"ok": True, "data": {"order_no": order.order_no, "status": order.status, "quantity": order.quantity}}

            if name == "get_production_status":
                order_no = arguments.get("order_no")
                production = (await session.execute(select(ProductionOrder).where(ProductionOrder.order_no == order_no))).scalar_one_or_none()
                if not production:
                    return {"ok": False, "error": "Production order not found"}
                return {"ok": True, "data": {"order_no": production.order_no, "status": production.status, "completed_quantity": production.completed_quantity}}

            if name == "search_knowledge":
                query = arguments.get("query", "")
                return {"ok": True, "data": {"query": query, "hint": "当前版本 MCP search_knowledge 返回最小示例响应，后续接入 RAG 检索链路。"}}

            return {"ok": False, "error": f"Unknown tool: {name}"}
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_server(SERVER))
