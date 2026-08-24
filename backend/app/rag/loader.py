from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from app.models.business import Document


def detect_source_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".md", ".markdown"}:
        return "md"
    if suffix in {".txt", ".text"}:
        return "txt"
    if suffix in {".pdf"}:
        return "pdf"
    return "txt"


def load_text_from_file(path: Path, source_type: str) -> str:
    if source_type == "pdf":
        import pdfplumber

        texts: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                texts.append(text)
        return "\n\n".join(texts)

    if source_type in {"md", "txt"}:
        return path.read_text(encoding="utf-8")

    return path.read_text(encoding="utf-8")


def file_checksum(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()
