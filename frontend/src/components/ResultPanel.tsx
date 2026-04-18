import type { QueryResponse } from "../types";

type ResultPanelProps = {
  result: QueryResponse | null;
};

export function ResultPanel({ result }: ResultPanelProps) {
  return (
    <section className="glass-card panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Generated Response</p>
          <h2>Evidence-backed answer</h2>
        </div>
      </div>
      {!result ? (
        <p className="empty-state">Submit a query to see the answer, retrieval evidence, query plan, and graph insights.</p>
      ) : (
        <div className="result-layout">
          <article className="answer-card">
            <h3>Answer</h3>
            <pre>{result.answer}</pre>
          </article>
          <article className="answer-card">
            <h3>Query plan</h3>
            <p className="muted">Rewritten query</p>
            <p>{result.query_plan.rewritten_query}</p>
            <p className="muted">Keywords</p>
            <div className="tag-row">
              {result.query_plan.keywords.map((keyword) => (
                <span key={keyword} className="entity-chip">
                  {keyword}
                </span>
              ))}
            </div>
          </article>
          <article className="answer-card">
            <h3>Graph insights</h3>
            {result.graph_insights.length ? (
              <ul className="flat-list">
                {result.graph_insights.map((insight) => (
                  <li key={insight}>{insight}</li>
                ))}
              </ul>
            ) : (
              <p className="muted">No graph neighbors were attached to this retrieval set.</p>
            )}
          </article>
          <article className="answer-card">
            <h3>Retrieved evidence</h3>
            <div className="retrieval-list">
              {result.retrieved_context.map((item) => (
                <div key={item.chunk_id} className="retrieval-card">
                  <div className="document-top">
                    <span className={`modality-tag modality-${item.modality}`}>{item.modality}</span>
                    <span className="tiny">score {(item.score * 100).toFixed(1)}%</span>
                  </div>
                  <h4>{item.title}</h4>
                  <p>{item.content}</p>
                </div>
              ))}
            </div>
          </article>
        </div>
      )}
    </section>
  );
}
