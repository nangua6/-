from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.rag.embeddings import EmbeddingProvider, MockEmbeddingProvider, OpenAICompatibleEmbeddingProvider
from app.rag.reranker import Reranker, SimpleScoreReranker
from app.rag.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        reranker: Reranker,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.reranker = reranker
        self.vector_store = vector_store

    async def retrieve(self, db: AsyncSession, query: str) -> dict[str, Any]:
        settings = get_settings()
        query_vec = (await self.embedding_provider.embed_texts([query]))[0]
        candidates = await self.vector_store.search(db, query_vec, top_k=settings.rag_top_k)

        documents = [item["content"] for item in candidates]
        reranked = await self.reranker.rerank(query, documents, top_k=settings.rag_rerank_top_k)

        results = []
        for item in reranked:
            candidate = candidates[item.index]
            results.append(
                {
                    "chunk_id": candidate["chunk_id"],
                    "document_id": candidate["document_id"],
                    "content": candidate["content"],
                    "score": item.score,
                    "section_title": candidate["section_title"],
                    "page_number": candidate["page_number"],
                    "source_title": candidate["source_title"],
                }
            )
        return {"query": query, "results": results}


def build_retriever() -> Retriever:
    settings = get_settings()
    if settings.embedding_provider == "openai" and settings.embedding_api_key:
        embedding = OpenAICompatibleEmbeddingProvider(settings.embedding_base_url, settings.embedding_api_key, settings.embedding_model, settings.request_timeout)
    else:
        embedding = MockEmbeddingProvider()
    return Retriever(embedding_provider=embedding, reranker=SimpleScoreReranker(), vector_store=VectorStore())
