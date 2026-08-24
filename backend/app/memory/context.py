from __future__ import annotations

from typing import Any


def compress_history(history: list[dict[str, Any]], max_messages: int = 20) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if len(history) <= max_messages:
        return history, {}
    overflow = history[:-max_messages]
    summary_text = f"已压缩历史消息 {len(overflow)} 条，其中包含用户和助手交互记录。"
    summary_memory = {"summary": summary_text, "count": len(overflow)}
    return history[-max_messages:], summary_memory
