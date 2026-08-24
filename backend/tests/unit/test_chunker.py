from __future__ import annotations

from app.rag.chunker import chunk_text


def test_chunk_respects_sections():
    text = """
# 标题一

这是第一段。

这是第二段。

# 标题二

这是第三段。
"""
    chunks = chunk_text(text, max_tokens=200, overlap_tokens=20, source_type="md")
    titles = {c.section_title for c in chunks}
    assert "标题一" in titles
    assert "标题二" in titles


def test_chunk_creates_overlap_for_long_text():
    text = "数据 " * 5000
    chunks = chunk_text(text, max_tokens=80, overlap_tokens=20, source_type="txt")
    assert len(chunks) >= 2
