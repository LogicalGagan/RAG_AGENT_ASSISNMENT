from __future__ import annotations

import time
from typing import Iterable

from pinecone import Pinecone, ServerlessSpec

from ..config import Settings
from .modality import ChunkPayload


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not self.settings.pinecone_api_key:
            print("WARNING: PINECONE_API_KEY is not set. VectorStore will be disabled.")
            self.pc = None
            self.index = None
            return

        self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
        self.index_name = self.settings.pinecone_index_name

        if self.index_name not in self.pc.list_indexes().names():
            print(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=512, # CLIP dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1' # Default fallback
                )
            )
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)

        self.index = self.pc.Index(self.index_name)

    def upsert_chunks(self, chunks: Iterable[ChunkPayload], embeddings: list[list[float]]) -> None:
        if not self.index:
            print("WARNING: Pinecone not configured. Chunks not saved.")
            return

        chunk_list = list(chunks)
        if not chunk_list:
            return

        vectors = []
        for chunk, embedding in zip(chunk_list, embeddings):
            vectors.append({
                "id": chunk.chunk_id,
                "values": embedding,
                "metadata": {
                    "document_id": chunk.document_id,
                    "title": chunk.title,
                    "modality": chunk.modality,
                    "content": chunk.content,
                    **chunk.metadata,
                }
            })

        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            self.index.upsert(vectors=vectors[i:i + batch_size])

    def query(self, query_embedding: list[float], top_k: int, selected_modalities: list[str]) -> list[dict]:
        if not self.index:
            return []

        filter_dict = {}
        if selected_modalities:
            filter_dict["modality"] = {"$in": selected_modalities}

        result = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter_dict if filter_dict else None,
            include_metadata=True,
        )

        hits: list[dict] = []
        for match in result.matches:
            hits.append(
                {
                    "chunk_id": match.id,
                    "content": match.metadata.get("content", ""),
                    "metadata": match.metadata,
                    "score": match.score,
                }
            )
        return hits

    def delete_document(self, document_id: str) -> None:
        if not self.index:
            return

        try:
            self.index.delete(filter={"document_id": {"$eq": document_id}})
        except Exception as e:
            print(f"Error deleting from pinecone: {e}")
