from __future__ import annotations

from typing import Iterable

from ..config import Settings
from ..utils.text import hashed_embedding

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency path
    OpenAI = None


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.use_openai and OpenAI else None

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        items = list(texts)
        if not items:
            return []

        if self.client:
            try:
                response = self.client.embeddings.create(
                    model=self.settings.openai_embedding_model,
                    input=items,
                )
                return [item.embedding for item in response.data]
            except Exception:
                # Fall back to deterministic local embeddings if the external API
                # is unavailable, quota-limited, or otherwise fails at runtime.
                self.client = None

        return [hashed_embedding(text) for text in items]

    def embed_query(self, text: str) -> list[float]:
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []
