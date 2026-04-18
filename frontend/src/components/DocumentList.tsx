import type { DocumentSummary } from "../types";

type DocumentListProps = {
  documents: DocumentSummary[];
};

export function DocumentList({ documents }: DocumentListProps) {
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
              <h3>{document.title}</h3>
              <p className="muted">{document.filename}</p>
              <div className="document-metrics">
                <span>{document.chunk_count} chunks</span>
                <span>{document.entity_count} entities</span>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
