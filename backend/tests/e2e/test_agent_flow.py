from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_login_then_agent_completion(client):
    login = await client.post("/api/auth/login", json={"username": "operator", "password": "Operator123!"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    session = await client.post("/api/sessions", json={"title": "demo"}, headers=headers)
    assert session.status_code == 200
    session_id = session.json()["id"]

    agent = await client.post("/api/agent/completions", json={"session_id": session_id, "message": "查询A001当前库存"}, headers=headers)
    assert agent.status_code == 200
    body = agent.json()
    assert "get_inventory" in body["tools_called"]
    assert body["answer"]
    assert body["trace_id"]
