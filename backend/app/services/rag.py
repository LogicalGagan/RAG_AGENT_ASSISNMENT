from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from fastapi import UploadFile

from ..config import Settings
from ..schemas import QueryPlan, QueryRequest, QueryResponse, RetrievalResult
from ..utils.text import extract_keywords
from .embedding import EmbeddingService
from .graph_store import GraphStore
from .llm import LLMService
from .modality import ModalityProcessor, ProcessedDocument
from .storage import DocumentRegistry
from .vector_store import VectorStore


class RAGOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.registry = DocumentRegistry(settings.registry_path)
        self.embedding_service = EmbeddingService(settings)
        self.llm_service = LLMService(settings)
        self.modality_processor = ModalityProcessor(settings, self.llm_service)
        self.vector_store = VectorStore(settings)
        self.graph_store = GraphStore(settings)

    async def ingest_files(self, files: Iterable[UploadFile]) -> list[dict]:
        ingested_records: list[dict] = []

        for upload in files:
            saved_path = await self._save_upload(upload)
            document = self.modality_processor.process(saved_path, original_filename=upload.filename)
            document.metadata["created_at"] = datetime.now(timezone.utc).isoformat()
            for chunk in document.chunks:
                chunk.metadata["created_at"] = document.metadata["created_at"]

            embeddings = self.embedding_service.embed_texts(chunk.content for chunk in document.chunks)
            self.vector_store.upsert_chunks(document.chunks, embeddings)
            self.graph_store.add_document(document)

            record = document.to_registry_record()
            self.registry.upsert_document(record)
            ingested_records.append(record)

        return ingested_records

    def query(self, request: QueryRequest) -> QueryResponse:
        plan = self._build_query_plan(request)
        query_embedding = self.embedding_service.embed_query(plan.rewritten_query)
        hits = self.vector_store.query(query_embedding, plan.top_k, plan.modality_filter)

        retrieved_context: list[RetrievalResult] = []
        citations: list[str] = []
        graph_insights: list[str] = []

        for hit in hits:
            metadata = hit["metadata"]
            graph_context = self.graph_store.expand_hit(
                document_id=metadata["document_id"],
                chunk_id=hit["chunk_id"],
                limit=self.settings.graph_neighbor_limit,
            )
            result = RetrievalResult(
                chunk_id=hit["chunk_id"],
                document_id=metadata["document_id"],
                title=metadata["title"],
                modality=metadata["modality"],
                score=hit["score"],
                content=hit["content"],
                graph_context=graph_context,
                metadata=metadata,
            )
            retrieved_context.append(result)
            citations.append(f"{result.title} [{result.modality}]")
            graph_insights.extend(graph_context)

        unique_insights = list(dict.fromkeys(graph_insights))
        answer = self.llm_service.generate_answer(request.question, plan, retrieved_context, unique_insights)

        return QueryResponse(
            answer=answer,
            query_plan=plan,
            retrieved_context=retrieved_context,
            graph_insights=unique_insights,
            citations=list(dict.fromkeys(citations)),
        )

    def list_documents(self) -> list[dict]:
        return self.registry.list_documents()

    def graph_summary(self) -> dict:
        return self.graph_store.summarize()

    async def _save_upload(self, upload: UploadFile) -> Path:
        destination = self.settings.uploads_dir / f"{uuid4()}-{upload.filename}"
        content = await upload.read()
        destination.write_bytes(content)
        return destination

    def _build_query_plan(self, request: QueryRequest) -> QueryPlan:
        question = request.question.strip()
        lowered = question.lower()
        modality_filter = [modality.lower() for modality in request.selected_modalities]
        if not modality_filter:
            for modality in ("image", "pdf", "text", "audio"):
                if modality in lowered:
                    modality_filter.append(modality)

        rewritten = question
        if modality_filter:
            rewritten = f"{question} Focus on modalities: {', '.join(modality_filter)}."

        return QueryPlan(
            rewritten_query=rewritten,
            modality_filter=modality_filter,
            keywords=extract_keywords(question),
            top_k=max(1, min(request.top_k or self.settings.query_top_k, 10)),
        )
