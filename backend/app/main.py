from __future__ import annotations

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
from app.core.logging import setup_logging  # noqa: F401


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Manufacturing Agent Platform", version="0.1.0")

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
