# RAG 设计

## 流程

1. 文档上传
2. 文档解析
3. 文本清洗
4. 结构化分块
5. Embedding
6. 向量存储
7. Top-K 召回
8. Rerank
9. Context 构建
10. LLM 回答 + Citation

## Chunk 策略

优先按 Heading / Paragraph / Section 拆分；过长文本再二次切分。

## 引用溯源

回答必须绑定 chunk、document、section、page。
