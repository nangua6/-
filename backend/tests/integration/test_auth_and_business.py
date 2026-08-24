from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_login_requires_existing_user(client):
    response = await client.post("/api/auth/login", json={"username": "no_user", "password": "no_pass"})
    assert response.status_code == 401


async def test_register_requires_auth(client):
    response = await client.post("/api/auth/register", json={"username": "new_user", "password": "123456"})
    assert response.status_code == 401
