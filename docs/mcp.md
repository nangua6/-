# MCP 设计说明

## MCP 是什么
MCP（Model Context Protocol）是一种用于向模型暴露工具、资源和上下文的开放协议。

## 本项目为什么使用 MCP
本项目希望通过标准协议暴露库存、订单、生产、知识检索等能力，使其不仅服务内部前端，也能被外部 Agent、IDE 或平台集成。

## MCP Tool 是什么
MCP Tool 是通过协议暴露的可调用函数，包含：
- name
- description
- inputSchema

## MCP 与传统 Function Calling 的区别
- Function Calling 通常绑定单一 LLM 调用链
- MCP 更像平台级工具暴露协议
- MCP 适合跨系统、跨客户端复用
