from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = "development"
    app_secret: str = "change-me"
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/app"
    database_echo: bool = False
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    cors_allow_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    ai_provider: str = "mock"
    ai_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str = ""
    ai_model: str = "gpt-4o-mini"
    ai_fallback_model: str = ""
    request_timeout: int = 30
    max_retries: int = 2

    embedding_provider: str = "mock"
    embedding_model: str = "text-embedding-3-small"
    embedding_base_url: str = ""
    embedding_api_key: str = ""

    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 120
    rag_top_k: int = 8
    rag_rerank_top_k: int = 4

    max_context_messages: int = 20


def get_settings() -> Settings:
    from dotenv import load_dotenv
    import os

    load_dotenv()
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_secret=os.getenv("APP_SECRET", "change-me"),
        database_url=os.getenv("DATABASE_URL", "postgresql+asyncpg://app:app@localhost:5432/app"),
        database_echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        jwt_secret=os.getenv("JWT_SECRET", "change-me"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "120")),
        cors_allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://localhost:3000").split(","),
        ai_provider=os.getenv("AI_PROVIDER", "mock"),
        ai_base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1"),
        ai_api_key=os.getenv("AI_API_KEY", ""),
        ai_model=os.getenv("AI_MODEL", "gpt-4o-mini"),
        ai_fallback_model=os.getenv("AI_FALLBACK_MODEL", ""),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        max_retries=int(os.getenv("MAX_RETRIES", "2")),
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "mock"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_base_url=os.getenv("EMBEDDING_BASE_URL", ""),
        embedding_api_key=os.getenv("EMBEDDING_API_KEY", ""),
        rag_chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "800")),
        rag_chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "120")),
        rag_top_k=int(os.getenv("RAG_TOP_K", "8")),
        rag_rerank_top_k=int(os.getenv("RAG_RERANK_TOP_K", "4")),
        max_context_messages=int(os.getenv("MAX_CONTEXT_MESSAGES", "20")),
    )
