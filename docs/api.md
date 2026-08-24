# API 文档

## 认证
- `POST /api/auth/login`
- `POST /api/auth/register`
- `GET /api/auth/me`

## 会话
- `GET /api/sessions`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}/messages`
- `POST /api/sessions/{session_id}/messages`

## 业务查询
- `GET /api/products`
- `GET /api/products/{product_code}`
- `GET /api/inventory`
- `GET /api/orders/{order_no}`
- `GET /api/production-orders/{order_no}`
- `GET /api/purchase-orders/{purchase_no}`
- `GET /api/customers/{customer_code}`

## Agent
- `POST /api/agent/completions`

## 知识库
- `GET /api/knowledge/documents`
- `POST /api/knowledge/upload`
- `GET /api/knowledge/documents/{document_id}/chunks`

## 可观测
- `GET /api/traces`
- `GET /api/traces/{trace_id}`
- `GET /api/dashboard`
