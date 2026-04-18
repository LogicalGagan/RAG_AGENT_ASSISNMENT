import type { GraphSummary } from "../types";
import { StatCard } from "./StatCard";

type GraphPanelProps = {
  graph: GraphSummary | null;
};

export function GraphPanel({ graph }: GraphPanelProps) {
  return (
    <section className="glass-card panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Knowledge Graph</p>
          <h2>Cross-modal relationship view</h2>
        </div>
      </div>
      {!graph ? (
        <p className="empty-state">Graph metrics will appear after the first ingestion run.</p>
      ) : (
        <>
          <div className="stats-grid">
            <StatCard label="Nodes" value={graph.total_nodes} helper="Documents, chunks, and entities" />
            <StatCard label="Edges" value={graph.total_edges} helper="Semantic and structural relationships" />
            <StatCard
              label="Modalities"
              value={Object.keys(graph.documents_by_modality).length || 0}
              helper="Currently represented in the graph"
            />
          </div>
          <div className="subsection">
            <h3>Documents by modality</h3>
            <div className="tag-row">
              {Object.entries(graph.documents_by_modality).map(([modality, count]) => (
                <span key={modality} className={`modality-tag modality-${modality}`}>
                  {modality}: {count}
                </span>
              ))}
            </div>
          </div>
          <div className="subsection">
            <h3>Top entities</h3>
            <div className="tag-row">
              {graph.top_entities.length ? (
                graph.top_entities.map((entity) => (
                  <span key={entity} className="entity-chip">
                    {entity}
                  </span>
                ))
              ) : (
                <p className="muted">Entity extraction will populate as richer content is ingested.</p>
              )}
            </div>
          </div>
        </>
      )}
    </section>
  );
}
