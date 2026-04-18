from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    title: str
    modality: str
    chunk_count: int
    entity_count: int
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    message: str
    documents: list[DocumentSummary]


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    selected_modalities: list[str] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    modality: str
    score: float
    content: str
    graph_context: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryPlan(BaseModel):
    rewritten_query: str
    modality_filter: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    query_plan: QueryPlan
    retrieved_context: list[RetrievalResult]
    graph_insights: list[str]
    citations: list[str]


class GraphSummary(BaseModel):
    total_nodes: int
    total_edges: int
    documents_by_modality: dict[str, int]
    top_entities: list[str]


class HealthResponse(BaseModel):
    status: str
    app: str
