# 仓库提交说明

## 项目目标
本项目是一个面向制造业企业内部员工的 AI Agent 平台，重点实现：
- 真实业务查询
- Tool Calling
- Agent 执行链路
- RAG 与引用溯源
- Trace / Evaluation / MCP

## 提交前检查
1. 确认 `.env` 未提交
2. 确认 `backend/.env` 未提交
3. 确认 `eval_results/` 未提交
4. 确认 `.venv` / `node_modules` 未提交
5. 确认 `docker compose up -d` 可启动
6. 确认 `/health` 正常
7. 确认测试通过

## 推荐展示顺序
1. 项目背景与目标
2. 架构图
3. Agent 执行流程
4. RAG 流程
5. Trace 与 Evaluation
6. 现场 Demo

## 面试重点
- 强调“LLM 负责理解，业务系统负责事实”
- 展示 Tool Calling 是真实数据库调用
- 展示 RAG 有 citation
- 展示 Trace 有执行链路
- 展示 Evaluation 有量化指标
