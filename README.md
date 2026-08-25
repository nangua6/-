# Manufacturing Agent Platform

制造业企业 AI Agent 平台 — 通过自然语言访问 ERP/MES 类业务数据。

## 项目定位

面向制造业企业内部员工的 AI Agent 平台，支持自然语言查询库存、订单、生产、采购等业务数据，结合企业知识库完成业务问答和分析。

## 核心功能

- **智能对话**：自然语言查询业务数据，Agent 自动调用工具
- **RAG 知识库**：文档上传、自动分块、向量检索、引用溯源
- **Trace 追踪**：完整的执行链路记录，包括工具调用、Token 消耗、延迟
- **运营仪表盘**：AI 请求量、成功率、成本等关键指标
- **MCP Server**：工具能力对外暴露

## 快速启动

无需 Docker，零依赖启动：

```bash
# 1. 后端
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 导入演示数据
cd ..
PYTHONPATH=backend python scripts/seed_demo.py

# 3. 启动后端
cd backend
uvicorn app.main:app --reload --host 127.0.0.1

# 4. 前端（新终端）
cd frontend
npm install
npm run dev
```

访问 `http://127.0.0.1:5173`

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | Admin123! |
| 操作员 | operator | Operator123! |

## 技术栈

- **后端**：FastAPI + SQLAlchemy + SQLite（零外部依赖）
- **前端**：React + TypeScript + Vite
- **AI**：支持 Mock 模式（开箱即用）和 OpenAI API
- **RAG**：向量检索 + 重排序 + 引用溯源

## 配置 AI

默认使用 Mock 模式，无需 API Key。如需接入真实模型，在 `backend/.env` 中配置：

```
AI_PROVIDER=openai
AI_API_KEY=sk-your-key
AI_MODEL=gpt-4o-mini
```

## 运行测试

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -m pytest -q
```

## 项目结构

```
manufacturing-agent-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── agents/       # Agent 服务
│   │   ├── ai/           # AI 模型提供者
│   │   ├── core/         # 配置、认证、依赖
│   │   ├── db/           # 数据库连接
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── rag/          # RAG 检索链路
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # 业务服务
│   │   └── tools/        # Agent 工具
│   ├── data/             # SQLite 数据库 + 上传文件
│   └── tests/
├── frontend/
│   └── src/
│       ├── pages/        # 页面组件
│       ├── api.ts        # API 客户端
│       └── App.tsx       # 主布局
├── scripts/              # 工具脚本
├── docs/                 # 项目文档
└── evals/                # 评测框架
```
