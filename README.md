# Manufacturing Agent Platform

制造业企业 AI Agent 平台。

## 项目定位

一个面向制造业企业内部员工的 AI Agent 平台，通过自然语言访问 ERP/MES 类业务数据，并结合企业知识库完成业务问答和分析。

## 当前完成状态

项目当前已实现：
- FastAPI 后端
- PostgreSQL + Redis 容器服务
- 用户认证与会话管理
- 真实业务 API
- Tool Calling
- Agent 执行链路
- RAG 上传、分块、检索、引用溯源
- Trace / Dashboard
- Evaluation 框架
- MCP Server 最小实现
- React 前端骨架

## 快速启动

```bash
cd manufacturing-agent-platform
docker compose up -d

# backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend
cd ../frontend
npm install
npm run dev

# mcp server
cd ../mcp_server
python3 -m venv .venv
source .venv/bin/activate
pip install mcp
PYTHONPATH=../backend python server.py
```

## 演示数据

```bash
cd manufacturing-agent-platform
PYTHONPATH=backend backend/.venv/bin/python scripts/seed_demo.py
```

默认账号：
- 管理员：`admin / Admin123!`
- 普通用户：`operator / Operator123!`

## 运行测试

```bash
cd manufacturing-agent-platform/backend
source .venv/bin/activate
PYTHONPATH=. python -m pytest -q
```

## 运行评测

```bash
cd manufacturing-agent-platform/backend
source .venv/bin/activate
PYTHONPATH=. python ../evals/run.py
```

## 面试重点展示

建议重点展示：
- Agent 如何调用 Tool
- RAG 如何返回引用
- Trace 如何记录执行链路
- Evaluation 如何量化效果
- MCP 如何暴露工具能力

## 核心文档

- `docs/architecture.md`
- `docs/api.md`
- `docs/agent.md`
- `docs/rag.md`
- `docs/mcp.md`
- `docs/security.md`
- `docs/code-review.md`
- `docs/interview.md`

## 后续优化方向

- 更完整前端 Trace 面板
- 真实模型端到端评测
- Streaming
- 更细粒度权限
- 多模型路由策略
- 更强 RAG 表格解析
