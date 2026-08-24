# Agent 设计

## 执行流程

1. 用户 Query 输入
2. 上下文加载
3. RAG 检索
4. System Prompt 构建
5. LLM 推理
6. Tool 选择与执行
7. Tool 结果回传
8. 必要时继续 Tool 循环
9. 最终回答生成
10. Trace 落库

## 防护设计

- 最大 Tool 轮数
- 最大 Tool 并发调用数
- Tool 超时
- Tool 异常捕获
- 不确定时拒答
- 输出结果基于工具与知识库
