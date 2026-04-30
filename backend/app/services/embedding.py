from __future__ import annotations

from typing import Iterable
from PIL import Image

from sentence_transformers import SentenceTransformer

from ..config import Settings

class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        print("Loading CLIP model (this may take a moment on first run)...")
        # clip-ViT-B-32 provides 512-dim embeddings for both text and images
        self.model = SentenceTransformer('clip-ViT-B-32')
        print("CLIP model loaded.")

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        items = list(texts)
        if not items:
            return []
        
        embeddings = self.model.encode(items, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, text: str) -> list[float]:
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []

    def embed_image(self, image_path: str) -> list[float]:
        image = Image.open(image_path)
        embedding = self.model.encode(image, convert_to_tensor=False)
        return embedding.tolist()
