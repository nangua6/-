from __future__ import annotations

import re
from typing import Any

from app.ai.provider import ChatMessage, ChatResult, ToolCall, ModelProvider

_CODE_RE = re.compile(r"GREE-[A-Z]{3}-\d{3}", re.IGNORECASE)
_ORDER_RE = re.compile(r"(SO|PO)\d{8,}", re.IGNORECASE)


class MockModelProvider(ModelProvider):
    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> ChatResult:
        user_text = ""
        system_text = ""
        for msg in messages:
            if msg.role == "system":
                system_text += "\n" + msg.content
            if msg.role == "user":
                user_text = msg.content

        tool_calls: list[ToolCall] = []
        content = ""

        if "库存" in user_text and tools:
            product_code = self._extract_code(user_text)
            tool_calls = [ToolCall(id="mock-1", name="get_inventory", arguments={"product_code": product_code or "GREE-CMP-001"})]
        elif ("延期" in user_text or "风险" in user_text) and tools:
            order_no = self._extract_order(user_text)
            tool_calls = [
                ToolCall(id="mock-2", name="get_order", arguments={"order_no": order_no or "SO20260801"}),
                ToolCall(id="mock-3", name="get_production_status", arguments={"order_no": order_no or "SO20260801"}),
                ToolCall(id="mock-4", name="analyze_order_risk", arguments={"order_no": order_no or "SO20260801"}),
            ]
        elif "订单" in user_text and tools:
            order_no = self._extract_order(user_text)
            tool_calls = [ToolCall(id="mock-5", name="get_order", arguments={"order_no": order_no or "SO20260801"})]
        elif "生产" in user_text and ("进度" in user_text or "状态" in user_text) and tools:
            order_no = self._extract_order(user_text)
            tool_calls = [ToolCall(id="mock-6", name="get_production_status", arguments={"order_no": order_no or "SO20260801"})]
        elif ("采购" in user_text or "供应商" in user_text) and tools:
            order_no = self._extract_order(user_text)
            tool_calls = [ToolCall(id="mock-7", name="get_purchase_order", arguments={"purchase_no": order_no or "PO20260801"})]
        elif "参考资料" in system_text and ("异常" in user_text or "处理" in user_text):
            content = "根据知识库检索到的生产异常处理要求，设备故障超过 2 小时需要启动异常生产流程，并同步通知相关团队评估影响。[1]"
        elif "产品" in user_text and tools:
            product_code = self._extract_code(user_text)
            tool_calls = [ToolCall(id="mock-8", name="get_product", arguments={"product_code": product_code or "GREE-CMP-001"})]
        else:
            content = "我是格力空调零部件智能助手，可以协助您查询：\n\n• 📦 **库存查询** — 如：查询 GREE-CMP-001 的库存\n• 📋 **订单查询** — 如：查看订单 SO20260801\n• 🏭 **生产进度** — 如：SO20260801 生产状态\n• 🛒 **采购订单** — 如：查看采购单 PO20260801\n• ⚠️ **延期风险** — 如：SO20260801 有延期风险吗\n• 📚 **知识库** — 如：生产异常如何处理"

        return ChatResult(
            content=content,
            tool_calls=tool_calls,
            input_tokens=len(user_text),
            output_tokens=len(content),
            model=model or "mock-model",
        )

    def _extract_code(self, text: str) -> str | None:
        match = _CODE_RE.search(text)
        return match.group(0).upper() if match else None

    def _extract_order(self, text: str) -> str | None:
        match = _ORDER_RE.search(text)
        return match.group(0).upper() if match else None
