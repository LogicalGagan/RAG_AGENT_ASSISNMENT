from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config import Settings
from .modality import ChunkPayload


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = self._create_client()
        self.collection = self._get_or_create_collection()

    def _create_client(self):
        try:
            return chromadb.PersistentClient(
                path=str(self.settings.chroma_dir),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        except Exception as exc:
            if not self._should_reset_store(exc):
                raise
            self._reset_store()
            return chromadb.PersistentClient(
                path=str(self.settings.chroma_dir),
                settings=ChromaSettings(anonymized_telemetry=False),
            )

    def _get_or_create_collection(self):
        return self.client.get_or_create_collection(
            name="multimodal_chunks",
            metadata={"hnsw:space": "cosine"},
        )

    def _should_reset_store(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return "default_tenant" in message or "no such table: tenants" in message

    def _reset_store(self) -> None:
        chroma_dir = Path(self.settings.chroma_dir)
        if chroma_dir.exists():
            shutil.rmtree(chroma_dir, ignore_errors=True)
        chroma_dir.mkdir(parents=True, exist_ok=True)

    def upsert_chunks(self, chunks: Iterable[ChunkPayload], embeddings: list[list[float]]) -> None:
        chunk_list = list(chunks)
        if not chunk_list:
            return

        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunk_list],
            documents=[chunk.content for chunk in chunk_list],
            metadatas=[
                {
                    "document_id": chunk.document_id,
                    "title": chunk.title,
                    "modality": chunk.modality,
                    **chunk.metadata,
                }
                for chunk in chunk_list
            ],
            embeddings=embeddings,
        )

    def query(self, query_embedding: list[float], top_k: int, selected_modalities: list[str]) -> list[dict]:
        where = {"modality": {"$in": selected_modalities}} if selected_modalities else None
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

        hits: list[dict] = []
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            hits.append(
                {
                    "chunk_id": chunk_id,
                    "content": document,
                    "metadata": metadata,
                    "score": 1.0 - float(distance),
                }
            )
        return hits

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})
