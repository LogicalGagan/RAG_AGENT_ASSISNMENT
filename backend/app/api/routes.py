from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from ..config import Settings, get_settings
from ..schemas import DocumentSummary, GraphSummary, HealthResponse, IngestResponse, QueryRequest, QueryResponse
from ..services.rag import RAGOrchestrator


router = APIRouter()


def get_orchestrator(settings: Settings = Depends(get_settings)) -> RAGOrchestrator:
    return RAGOrchestrator(settings)


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name)


@router.get("/documents", response_model=list[DocumentSummary])
def list_documents(orchestrator: RAGOrchestrator = Depends(get_orchestrator)) -> list[DocumentSummary]:
    return [DocumentSummary(**document) for document in orchestrator.list_documents()]


@router.get("/graph", response_model=GraphSummary)
def graph_summary(orchestrator: RAGOrchestrator = Depends(get_orchestrator)) -> GraphSummary:
    return GraphSummary(**orchestrator.graph_summary())


@router.post("/ingest", response_model=IngestResponse)
async def ingest_files(
    files: list[UploadFile] = File(...),
    orchestrator: RAGOrchestrator = Depends(get_orchestrator),
) -> IngestResponse:
    documents = await orchestrator.ingest_files(files)
    return IngestResponse(message=f"Ingested {len(documents)} files successfully.", documents=documents)


@router.post("/query", response_model=QueryResponse)
def query(
    payload: QueryRequest,
    orchestrator: RAGOrchestrator = Depends(get_orchestrator),
) -> QueryResponse:
    return orchestrator.query(payload)
