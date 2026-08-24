from __future__ import annotations

import math
import random
from typing import Any

import httpx


class EmbeddingProvider:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 32) -> None:
        self.dimension = dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            random.seed(hash(text))
            vec = [random.random() for _ in range(self.dimension)]
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            vectors.append([x / norm for x in vec])
        return vectors


class OpenAICompatibleEmbeddingProvider(EmbeddingProvider):
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        resp = await self._client.post("/embeddings", json={"model": self.model, "input": texts})
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]
