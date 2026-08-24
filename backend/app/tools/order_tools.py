from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Order, ProductionOrder, PurchaseOrder, Customer
from app.tools.base import BaseTool, ToolContext, ToolResult


class GetOrderTool(BaseTool):
    name = "get_order"
    description = "根据订单号查询订单详情"

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {"order_no": {"type": "string"}}, "required": ["order_no"]},
        }

    async def run(self, ctx: ToolContext, arguments: dict[str, Any], db: AsyncSession) -> ToolResult:
        order_no = arguments.get("order_no")
        if not order_no:
            return ToolResult(ok=False, error="order_no is required")
        order = (await db.execute(select(Order).where(Order.order_no == order_no))).scalar_one_or_none()
        if not order:
            return ToolResult(ok=False, error="Order not found")
        customer = await db.get(Customer, order.customer_id)
        return ToolResult(ok=True, data={
            "order_no": order.order_no,
            "status": order.status,
            "quantity": order.quantity,
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
            "customer_code": customer.customer_code if customer else None,
            "product_id": order.product_id,
        })


class GetProductionStatusTool(BaseTool):
    name = "get_production_status"
    description = "查询订单对应的生产进度"

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {"order_no": {"type": "string"}}, "required": ["order_no"]},
        }

    async def run(self, ctx: ToolContext, arguments: dict[str, Any], db: AsyncSession) -> ToolResult:
        order_no = arguments.get("order_no")
        if not order_no:
            return ToolResult(ok=False, error="order_no is required")
        production = (await db.execute(select(ProductionOrder).where(ProductionOrder.order_no == order_no))).scalar_one_or_none()
        if not production:
            return ToolResult(ok=False, error="Production order not found")
        return ToolResult(ok=True, data={
            "order_no": production.order_no,
            "status": production.status,
            "planned_quantity": production.planned_quantity,
            "completed_quantity": production.completed_quantity,
            "planned_date": production.planned_date.isoformat() if production.planned_date else None,
            "completed_date": production.completed_date.isoformat() if production.completed_date else None,
        })


class GetPurchaseOrderTool(BaseTool):
    name = "get_purchase_order"
    description = "根据采购单号查询采购信息"

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {"purchase_no": {"type": "string"}}, "required": ["purchase_no"]},
        }

    async def run(self, ctx: ToolContext, arguments: dict[str, Any], db: AsyncSession) -> ToolResult:
        purchase_no = arguments.get("purchase_no")
        if not purchase_no:
            return ToolResult(ok=False, error="purchase_no is required")
        purchase = (await db.execute(select(PurchaseOrder).where(PurchaseOrder.purchase_no == purchase_no))).scalar_one_or_none()
        if not purchase:
            return ToolResult(ok=False, error="Purchase order not found")
        return ToolResult(ok=True, data={
            "purchase_no": purchase.purchase_no,
            "supplier": purchase.supplier,
            "status": purchase.status,
            "quantity": purchase.quantity,
            "expected_date": purchase.expected_date.isoformat() if purchase.expected_date else None,
        })


class GetCustomerTool(BaseTool):
    name = "get_customer"
    description = "根据客户编码查询客户信息"

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {"customer_code": {"type": "string"}}, "required": ["customer_code"]},
        }

    async def run(self, ctx: ToolContext, arguments: dict[str, Any], db: AsyncSession) -> ToolResult:
        customer_code = arguments.get("customer_code")
        if not customer_code:
            return ToolResult(ok=False, error="customer_code is required")
        customer = (await db.execute(select(Customer).where(Customer.customer_code == customer_code))).scalar_one_or_none()
        if not customer:
            return ToolResult(ok=False, error="Customer not found")
        return ToolResult(ok=True, data={
            "customer_code": customer.customer_code,
            "customer_name": customer.customer_name,
            "level": customer.level,
        })
