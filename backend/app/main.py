from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.sessions import router as sessions_router
from app.api.messages import router as messages_router
from app.api.business import router as business_router
from app.api.agent import router as agent_router
from app.api.knowledge import router as knowledge_router
from app.api.traces import router as traces_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import build_engine, build_session_factory
from app.db.base import Base

# Import all models so they register with Base
import app.models.user  # noqa: F401
import app.models.session  # noqa: F401
import app.models.message  # noqa: F401
import app.models.business  # noqa: F401
import app.models.trace  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # Ensure data directory exists for SQLite
    if settings.database_url.startswith("sqlite"):
        db_path = Path(settings.database_url.split("///", 1)[1])
        db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = build_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    setup_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Manufacturing Agent Platform", version="0.2.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(sessions_router)
    app.include_router(messages_router)
    app.include_router(business_router)
    app.include_router(agent_router)
    app.include_router(knowledge_router)
    app.include_router(traces_router)

    return app


app = create_app()
