import type { DocumentSummary } from "../types";

type DocumentListProps = {
  documents: DocumentSummary[];
  onDelete: (documentId: string) => void;
  deletingId: string | null;
};

export function DocumentList({ documents, onDelete, deletingId }: DocumentListProps) {
  return (
    <section className="glass-card panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Indexed Assets</p>
          <h2>Knowledge base inventory</h2>
        </div>
        <span className="pill">{documents.length} files</span>
      </div>
      <div className="document-list">
        {documents.length === 0 ? (
          <p className="empty-state">Upload text, PDFs, or images to start building the graph-backed vector store.</p>
        ) : (
          documents.map((document) => (
            <article key={document.document_id} className="document-card">
              <div className="document-top">
                <span className={`modality-tag modality-${document.modality}`}>{document.modality}</span>
                <span className="tiny">{new Date(document.created_at).toLocaleString()}</span>
              </div>
              <div className="document-body">
                <h3>{document.title}</h3>
                <p className="muted document-filename">{document.filename}</p>
              </div>
              <div className="document-metrics">
                <span>{document.chunk_count} chunks</span>
                <span>{document.entity_count} entities</span>
              </div>
              <button
                type="button"
                className="danger-button"
                onClick={() => onDelete(document.document_id)}
                disabled={deletingId === document.document_id}
              >
                {deletingId === document.document_id ? "Removing..." : "Remove File"}
              </button>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
