from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_admin_can_upload_and_agent_can_use_rag(client):
    login = await client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    content = "# 生产异常处理规范\n设备故障超过 2 小时需要启动异常生产流程。\n".encode("utf-8")
    upload = await client.post("/api/knowledge/upload", files={"file": ("生产异常处理规范.md", content, "text/markdown")}, headers=headers)
    assert upload.status_code == 200

    session = await client.post("/api/sessions", json={"title": "rag"}, headers=headers)
    session_id = session.json()["id"]

    agent = await client.post("/api/agent/completions", json={"session_id": session_id, "message": "设备故障超过2小时应该怎么处理？"}, headers=headers)
    assert agent.status_code == 200
    body = agent.json()
    assert body["citations"]
    assert "异常" in body["answer"]
