from __future__ import annotations

import math
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import DocumentChunk, Embedding, Document


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y
    denom = math.sqrt(norm_a) * math.sqrt(norm_b)
    return dot / denom if denom else 0.0


class VectorStore:
    async def insert_embeddings(self, db: AsyncSession, chunk_ids: list[str], vectors: list[list[float]], model: str) -> None:
        for chunk_id, vector in zip(chunk_ids, vectors):
            db.add(Embedding(chunk_id=chunk_id, model=model, vector=vector))
        await db.flush()

    async def search(self, db: AsyncSession, query_vector: list[float], top_k: int = 8) -> list[dict[str, Any]]:
        rows = (await db.execute(select(DocumentChunk, Embedding).join(Embedding, Embedding.chunk_id == DocumentChunk.id))).all()
        scored: list[tuple[float, DocumentChunk, Embedding]] = []
        for chunk, emb in rows:
            score = cosine_similarity(query_vector, emb.vector or [])
            scored.append((score, chunk, emb))
        scored.sort(key=lambda x: x[0], reverse=True)

        results: list[dict[str, Any]] = []
        seen_docs: set[str] = set()
        for score, chunk, emb in scored[: top_k * 2]:
            if chunk.document_id in seen_docs:
                continue
            seen_docs.add(chunk.document_id)
            doc = await db.get(Document, chunk.document_id)
            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "score": round(score, 6),
                    "section_title": chunk.section_title,
                    "page_number": chunk.page_number,
                    "source_title": doc.title if doc else "",
                }
            )
            if len(results) >= top_k:
                break
        return results
