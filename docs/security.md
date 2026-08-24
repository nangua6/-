# 安全设计

## 关键风险

- Prompt Injection
- Tool Injection
- SQL Injection
- 权限绕过
- API Key 泄露
- 模型幻觉
- 无限 Tool 循环

## 当前策略

- API 参数使用 Pydantic 校验
- SQL 使用 ORM 参数化查询
- Tool 有权限检查
- RAG 内容视为不可信上下文
- 系统 Prompt 优先级高于检索内容
- 环境变量管理 API Key
- Agent 设置最大执行轮数与超时
