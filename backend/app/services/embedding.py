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
        self.model = SentenceTransformer('clip-ViT-B-32', device='cpu')
        self.model.max_seq_length = 77  # Force truncation to prevent PDF indexing crashes
        print("CLIP model loaded.")

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        import re
        items = list(texts)
        if not items:
            return []
            
        safe_texts = []
        for text in items:
            # Clean weird symbols from CSV/PDF that explode token counts
            clean_text = re.sub(r'[^A-Za-z0-9\s.,?!-]', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            # Hard limit to ~200 characters to safely stay under CLIP's 77 token limit
            safe_texts.append(clean_text[:200])
        
        embeddings = self.model.encode(safe_texts, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, text: str) -> list[float]:
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []

    def embed_image(self, image_path: str) -> list[float]:
        image = Image.open(image_path)
        embedding = self.model.encode(image, convert_to_tensor=False)
        return embedding.tolist()
