from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.business import Document, DocumentChunk
from app.rag.chunker import chunk_text
from app.rag.embeddings import MockEmbeddingProvider, OpenAICompatibleEmbeddingProvider
from app.rag.loader import detect_source_type, file_checksum, load_text_from_file
from app.rag.vector_store import VectorStore


async def import_document_from_path(db: AsyncSession, path: Path, title: str | None = None, created_by: str | None = None) -> dict[str, Any]:
    source_type = detect_source_type(path.name)
    checksum = file_checksum(path)
    exists = (await db.execute(select(Document).where(Document.checksum == checksum))).scalar_one_or_none()
    if exists:
        return {"status": "skipped", "document_id": exists.id}

    text = load_text_from_file(path, source_type)
    settings = get_settings()
    chunks = chunk_text(text, max_tokens=settings.rag_chunk_size, overlap_tokens=settings.rag_chunk_overlap, source_type=source_type)

    doc = Document(title=title or path.name, source_type=source_type, path=str(path), checksum=checksum, created_by=created_by)
    db.add(doc)
    await db.flush()

    chunk_ids: list[str] = []
    texts: list[str] = []
    for chunk in chunks:
        row = DocumentChunk(document_id=doc.id, chunk_index=chunk.chunk_index, content=chunk.content, page_number=chunk.page_number, section_title=chunk.section_title, token_count=chunk.token_count)
        db.add(row)
        await db.flush()
        chunk_ids.append(row.id)
        texts.append(chunk.content)

    if settings.embedding_provider == "openai" and settings.embedding_api_key:
        provider = OpenAICompatibleEmbeddingProvider(settings.embedding_base_url, settings.embedding_api_key, settings.embedding_model, settings.request_timeout)
    else:
        provider = MockEmbeddingProvider()

    vectors = await provider.embed_texts(texts)
    await VectorStore().insert_embeddings(db, chunk_ids, vectors, settings.embedding_model)
    await db.commit()
    return {"status": "imported", "document_id": doc.id, "chunks": len(chunk_ids)}
