from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Order, ProductionOrder, Inventory
from app.tools.base import BaseTool, ToolContext, ToolResult


class AnalyzeOrderRiskTool(BaseTool):
    name = "analyze_order_risk"
    description = "根据订单、生产与库存信息分析延期风险"

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
        production = (await db.execute(select(ProductionOrder).where(ProductionOrder.order_no == order_no))).scalar_one_or_none()
        stock_qty = 0
        inv = (await db.execute(select(Inventory.quantity).where(Inventory.product_id == order.product_id))).scalars().all()
        stock_qty = sum(inv)

        reason = []
        risk_score = 0
        completion_rate = 0.0
        if production and production.planned_quantity:
            completion_rate = production.completed_quantity / production.planned_quantity
            if completion_rate < 0.8:
                reason.append(f"生产完成率仅为 {completion_rate:.0%}")
                risk_score += 2
        else:
            reason.append("未找到生产订单或计划数量为空")
            risk_score += 2

        if order.delivery_date:
            days_left = (order.delivery_date - date.today()).days
            if days_left < 3:
                reason.append(f"距离交付日期仅剩 {days_left} 天")
                risk_score += 2
            elif days_left < 7:
                reason.append(f"交付日期较近，剩余 {days_left} 天")
                risk_score += 1
        else:
            reason.append("订单缺少交付日期")

        if stock_qty <= 0:
            reason.append("当前库存为 0")
            risk_score += 1

        risk_level = "LOW"
        if risk_score >= 4:
            risk_level = "HIGH"
        elif risk_score >= 2:
            risk_level = "MEDIUM"

        return ToolResult(ok=True, data={
            "order_no": order.order_no,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "completion_rate": round(completion_rate, 4),
            "stock_quantity": stock_qty,
            "reason": reason,
        })
