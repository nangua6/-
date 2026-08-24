from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_payload, require_admin
from app.models.business import Document, DocumentChunk, Embedding
from app.services.knowledge_service import import_document_from_path

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/documents")
async def list_documents(_payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    docs = (await db.execute(select(Document).order_by(Document.created_at.desc()))).scalars().all()
    return [{"id": d.id, "title": d.title, "source_type": d.source_type, "created_at": d.created_at.isoformat()} for d in docs]


@router.post("/upload")
async def upload_document(file: UploadFile, _admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    target = UPLOAD_DIR / file.filename
    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return await import_document_from_path(db, target, title=file.filename, created_by=_admin.get("sub"))


@router.get("/documents/{document_id}/chunks")
async def document_chunks(document_id: str, _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    chunks = (await db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index))).scalars().all()
    return [{"id": c.id, "chunk_index": c.chunk_index, "section_title": c.section_title, "page_number": c.page_number, "content": c.content} for c in chunks]
