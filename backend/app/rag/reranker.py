from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RerankItem:
    index: int
    score: float
    content: str


class Reranker:
    async def rerank(self, query: str, documents: list[str], top_k: int = 4) -> list[RerankItem]:
        raise NotImplementedError


class SimpleScoreReranker(Reranker):
    async def rerank(self, query: str, documents: list[str], top_k: int = 4) -> list[RerankItem]:
        query_tokens = set(query.lower().split())
        items: list[RerankItem] = []
        for idx, text in enumerate(documents):
            doc_tokens = set(text.lower().split())
            overlap = len(query_tokens & doc_tokens)
            score = overlap / (len(query_tokens) + 1e-9)
            length_bonus = min(1.0, len(text) / 800)
            items.append(RerankItem(index=idx, score=score + length_bonus * 0.01, content=text))
        items.sort(key=lambda x: x.score, reverse=True)
        return items[:top_k]
