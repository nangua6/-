# MCP Server

## 什么是 MCP
MCP（Model Context Protocol）是一种用于向模型暴露工具、资源和上下文的开放协议。

## 本项目为什么使用 MCP
本项目通过 MCP 暴露核心业务工具，让外部 Agent 或 IDE 能以统一协议访问库存、订单和知识检索能力。

## MCP Tool 是什么
MCP Tool 是通过协议暴露的可调用函数，拥有名称、描述和 JSON Schema 输入定义。

## MCP 与传统 Function Calling 的区别
- Function Calling 通常绑定在单一 LLM 调用流程中
- MCP 提供跨系统的标准化工具暴露方式
- MCP 更适合企业平台化、可复用、可审计场景

## 如何运行
```bash
cd manufacturing-agent-platform/mcp_server
python3 -m venv .venv
source .venv/bin/activate
pip install mcp
PYTHONPATH=../backend python server.py
```

当前示例至少暴露：
- `get_inventory`
- `get_order`
- `get_production_status`
- `search_knowledge`
