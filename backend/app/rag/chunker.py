from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Chunk:
    content: str
    section_title: str | None
    page_number: int | None
    chunk_index: int
    token_count: int


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_BLANK_LINE_RE = re.compile(r"\n\s*\n")


def estimate_token_count(text: str) -> int:
    return max(1, len(text) // 4)


def chunk_text(
    text: str,
    *,
    max_tokens: int = 800,
    overlap_tokens: int = 120,
    source_type: str = "md",
) -> list[Chunk]:
    sections = split_sections(text, source_type=source_type)
    chunks: list[Chunk] = []
    idx = 0
    for section in sections:
        parts = split_section_content(section.content, max_tokens=max_tokens, overlap_tokens=overlap_tokens)
        for part in parts:
            chunks.append(
                Chunk(
                    content=part,
                    section_title=section.title,
                    page_number=section.page_number,
                    chunk_index=idx,
                    token_count=estimate_token_count(part),
                )
            )
            idx += 1
    return chunks


@dataclass
class Section:
    title: str | None
    page_number: int | None
    content: str


def split_sections(text: str, *, source_type: str = "md") -> list[Section]:
    if source_type == "pdf":
        return _split_pdf_sections(text)
    return _split_markdown_sections(text)


def _split_markdown_sections(text: str) -> list[Section]:
    lines = text.splitlines()
    sections: list[Section] = []
    current_title: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append(Section(title=current_title, page_number=None, content=content))

    for line in lines:
        heading = _HEADING_RE.match(line)
        if heading:
            flush()
            current_title = heading.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    flush()

    if not sections:
        sections.append(Section(title=None, page_number=None, content=text.strip()))
    return sections


def _split_pdf_sections(text: str) -> list[Section]:
    pages = [page.strip() for page in text.split("\f") if page.strip()]
    sections: list[Section] = []
    for idx, page in enumerate(pages, start=1):
        sections.append(Section(title=f"Page {idx}", page_number=idx, content=page))
    if not sections and text.strip():
        sections.append(Section(title=None, page_number=None, content=text.strip()))
    return sections


def split_section_content(text: str, *, max_tokens: int, overlap_tokens: int) -> Iterable[str]:
    paragraphs = [chunk.strip() for chunk in _BLANK_LINE_RE.split(text) if chunk.strip()]
    buffer = ""
    results: list[str] = []

    for para in paragraphs:
        candidate = f"{buffer}\n\n{para}".strip() if buffer else para
        if estimate_token_count(candidate) <= max_tokens:
            buffer = candidate
            continue

        if buffer:
            results.append(buffer)
        if estimate_token_count(para) <= max_tokens:
            buffer = para
            continue

        results.extend(_hard_split(para, max_tokens=max_tokens, overlap_tokens=overlap_tokens))
        buffer = ""

    if buffer:
        results.append(buffer)
    return results


def _hard_split(text: str, *, max_tokens: int, overlap_tokens: int) -> list[str]:
    approx_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4
    results: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + approx_chars)
        results.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap_chars)
    return results
