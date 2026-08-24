from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
import app.models  # noqa: F401
from app.ai.mock_provider import MockModelProvider
from app.agents.agent_service import AgentService
from app.rag.retriever import Retriever
from app.rag.reranker import SimpleScoreReranker
from app.rag.vector_store import VectorStore
from app.rag.embeddings import MockEmbeddingProvider
from app.tools.registry import default_tool_registry
from app.tools.base import ToolContext


@pytest_asyncio.fixture()
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_mock_agent_calls_inventory_tool(db_session: AsyncSession):
    agent = AgentService(
        provider=MockModelProvider(),
        tool_registry=default_tool_registry(),
        retriever=Retriever(embedding_provider=MockEmbeddingProvider(), reranker=SimpleScoreReranker(), vector_store=VectorStore()),
    )
    result = await agent.run(user_message="查询A001当前库存", history=[], system_prompt="测试", db=db_session, ctx=ToolContext(role="USER"))
    assert "get_inventory" in result.tools_called
    assert result.trace_id


@pytest.mark.asyncio
async def test_mock_agent_default_message_without_keyword(db_session: AsyncSession):
    agent = AgentService(
        provider=MockModelProvider(),
        tool_registry=default_tool_registry(),
        retriever=Retriever(embedding_provider=MockEmbeddingProvider(), reranker=SimpleScoreReranker(), vector_store=VectorStore()),
    )
    result = await agent.run(user_message="你好", history=[], system_prompt="测试", db=db_session, ctx=ToolContext(role="USER"))
    assert result.answer
    assert result.tools_called == []
