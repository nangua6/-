from __future__ import annotations

import re
from typing import Any

from app.ai.provider import ChatMessage, ChatResult, ToolCall, ModelProvider


_ORDER_RE = re.compile(r"(SO|PO)\d+", re.IGNORECASE)
_CODE_RE = re.compile(r"[A-Za-z]\d{2,}")


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
            tool_calls = [ToolCall(id="mock-1", name="get_inventory", arguments={"product_code": product_code or "A001"})]
        elif "延期" in user_text and tools:
            order_no = self._extract_order(user_text)
            tool_calls = [
                ToolCall(id="mock-2", name="get_order", arguments={"order_no": order_no or "SO20260001"}),
                ToolCall(id="mock-3", name="get_production_status", arguments={"order_no": order_no or "SO20260001"}),
                ToolCall(id="mock-4", name="analyze_order_risk", arguments={"order_no": order_no or "SO20260001"}),
            ]
        elif "订单" in user_text and tools:
            order_no = self._extract_order(user_text)
            tool_calls = [ToolCall(id="mock-5", name="get_order", arguments={"order_no": order_no or "SO20260001"})]
        elif "参考资料" in system_text and ("异常" in user_text or "处理" in user_text):
            content = "根据知识库检索到的生产异常处理要求，设备故障超过 2 小时需要启动异常生产流程，并同步通知相关团队评估影响。[1]"
        else:
            content = "我可以协助查询库存、订单、生产和知识库。请提供业务编号或更具体的问题。"

        return ChatResult(
            content=content,
            tool_calls=tool_calls,
            input_tokens=len(user_text),
            output_tokens=len(content),
            model=model or "mock-model",
        )

    def _extract_code(self, text: str) -> str | None:
        match = _CODE_RE.search(text)
        return match.group(0) if match else None

    def _extract_order(self, text: str) -> str | None:
        match = _ORDER_RE.search(text)
        return match.group(0) if match else None
