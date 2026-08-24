from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.db.session import build_engine, build_session_factory
from app.main import app
from app.core import deps


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture()
async def client():
    settings = get_settings()
    engine = build_engine(settings, use_pool=False)
    session_factory = build_session_factory(engine)

    async def _override_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[deps.get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(deps.get_db, None)
    await engine.dispose()
