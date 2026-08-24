# 架构设计

## 总体定位

本项目是一个面向制造业企业内部员工的 AI Agent 平台，核心理念是：

- **LLM 负责理解与决策**
- **业务系统负责事实与执行**
- **知识库负责制度与规范参考**

## 分层结构

1. 前端层：React + Vite + TypeScript
2. API 层：FastAPI
3. Agent 层：任务规划、工具调用、上下文管理
4. Tool 层：业务工具执行
5. RAG 层：文档解析、分块、Embedding、检索、Rerank、引用溯源
6. 数据层：PostgreSQL、Redis
7. 可观测层：Trace、Token、Cost、Evaluation

## 数据流

用户 Query
-> API Gateway
-> Session / Memory
-> Agent Planner
-> Tool Execution / RAG Retrieval
-> Response Builder
-> Final Answer + Citation + Trace
