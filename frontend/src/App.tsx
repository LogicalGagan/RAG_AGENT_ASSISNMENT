import { useEffect, useState, type FormEvent } from "react";

import { DocumentList } from "./components/DocumentList";
import { GraphPanel } from "./components/GraphPanel";
import { QueryWorkspace } from "./components/QueryWorkspace";
import { ResultPanel } from "./components/ResultPanel";
import { StatCard } from "./components/StatCard";
import { deleteDocument, fetchDocuments, fetchGraphSummary, uploadFiles } from "./lib";
import type { DocumentSummary, GraphSummary, QueryResponse } from "./types";

const pipelineSteps = [
  "1. Multi-modal ingestion for text, PDF, image, and optional audio inputs",
  "2. Chunking plus embedding generation, stored in ChromaDB",
  "3. Entity extraction and relationship construction in a NetworkX knowledge graph",
  "4. Query planning, top-k retrieval, graph expansion, and LLM grounded response generation",
];

export default function App() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [graph, setGraph] = useState<GraphSummary | null>(null);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function refreshData() {
    try {
      const [documentResponse, graphResponse] = await Promise.all([fetchDocuments(), fetchGraphSummary()]);
      setDocuments(documentResponse);
      setGraph(graphResponse);
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : "Failed to load backend data.");
    }
  }

  useEffect(() => {
    void refreshData();
  }, []);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFiles.length) {
      return;
    }

    setUploading(true);
    setError("");
    try {
      await uploadFiles(selectedFiles);
      setSelectedFiles([]);
      await refreshData();
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(documentId: string) {
    setDeletingId(documentId);
    setError("");
    try {
      await deleteDocument(documentId);
      setResult((current) =>
        current && current.retrieved_context.some((item) => item.document_id === documentId) ? null : current,
      );
      await refreshData();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Delete failed.");
    } finally {
      setDeletingId(null);
    }
  }

  const indexedCount = documents.length;
  const modalityCount = Object.keys(graph?.documents_by_modality ?? {}).length;
  const nodeCount = graph?.total_nodes ?? 0;

  return (
    <main className="app-shell">
      <section className="topbar">
        <div className="brand-block">
          <p className="eyebrow">Academic Assignment Build</p>
          <div className="brand-row">
            <div className="brand-mark">MM</div>
            <div>
              <h1 className="brand-title">Multi-Modal Graph RAG</h1>
              <p className="brand-subtitle">Grounded retrieval across files, images, and graph relationships</p>
            </div>
          </div>
        </div>
        <div className="topbar-status">
          <div className="status-pill">
            <span className="status-dot" />
            Ready for live demo
          </div>
          <p className="muted">Dockerized full-stack app with local Ollama and graph-backed retrieval.</p>
        </div>
      </section>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">End-to-End Assignment Demo</p>
          <h2 className="hero-title">Ask questions over text, PDFs, and images with retrieval plus graph context.</h2>
          <p className="hero-text">
            A full-stack Retrieval Augmented Generation platform with vector search, graph-based context expansion,
            and cross-modal ingestion across text, PDFs, images, and optional audio.
          </p>
          <div className="hero-highlights">
            <span className="feature-chip">Chroma retrieval</span>
            <span className="feature-chip">NetworkX graph</span>
            <span className="feature-chip">Ollama generation</span>
            <span className="feature-chip">Docker-ready demo</span>
          </div>
        </div>
        <div className="hero-stats">
          <StatCard label="Indexed Files" value={indexedCount} helper="Current knowledge base assets" />
          <StatCard label="Modalities" value={modalityCount} helper="Represented across the graph" />
          <StatCard label="Graph Nodes" value={nodeCount} helper="Documents, chunks, and entities tracked" />
        </div>
      </section>

      <section className="glass-card panel atmospheric-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Pipeline</p>
            <h2>Architecture at a glance</h2>
          </div>
          <span className="pill accent-pill">Production-style flow</span>
        </div>
        <div className="pipeline-grid">
          {pipelineSteps.map((step) => (
            <article key={step} className="pipeline-card">
              <p>{step}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="workspace-grid">
        <div className="workspace-column">
          <section className="glass-card panel upload-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Ingestion</p>
                <h2>Upload multi-modal files</h2>
              </div>
              <span className="pill">{selectedFiles.length} selected</span>
            </div>
            <form className="upload-form" onSubmit={handleUpload}>
              <label className="upload-zone">
                <input
                  type="file"
                  multiple
                  accept=".txt,.md,.csv,.json,.pdf,.png,.jpg,.jpeg,.webp,.bmp,.gif,.mp3,.wav,.m4a,.ogg,.flac"
                  onChange={(event) => setSelectedFiles(Array.from(event.target.files || []))}
                />
                <span>{selectedFiles.length ? `${selectedFiles.length} file(s) selected` : "Choose text, PDF, image, or audio files"}</span>
                <small>Text and PDF are parsed directly. Images use Ollama vision when available, then become searchable text.</small>
              </label>
              {selectedFiles.length ? (
                <div className="selected-file-grid">
                  {selectedFiles.map((file) => (
                    <div key={`${file.name}-${file.size}`} className="selected-file-pill">
                      <strong>{file.name}</strong>
                      <span>{Math.max(1, Math.round(file.size / 1024))} KB</span>
                    </div>
                  ))}
                </div>
              ) : null}
              <button type="submit" className="primary-button" disabled={uploading || !selectedFiles.length}>
                {uploading ? "Indexing files..." : "Ingest Into Graph RAG"}
              </button>
            </form>
            {error ? <p className="error-text">{error}</p> : null}
          </section>

          <DocumentList documents={documents} onDelete={handleDelete} deletingId={deletingId} />
          <GraphPanel graph={graph} />
        </div>

        <div className="workspace-column">
          <QueryWorkspace onResult={setResult} />
          <ResultPanel result={result} />
        </div>
      </section>
    </main>
  );
}
