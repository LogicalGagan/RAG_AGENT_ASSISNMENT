export type DocumentSummary = {
  document_id: string;
  filename: string;
  title: string;
  modality: string;
  chunk_count: number;
  entity_count: number;
  created_at: string;
  metadata: Record<string, string | number | boolean | null>;
};

export type GraphSummary = {
  total_nodes: number;
  total_edges: number;
  documents_by_modality: Record<string, number>;
  top_entities: string[];
};

export type RetrievalResult = {
  chunk_id: string;
  document_id: string;
  title: string;
  modality: string;
  score: number;
  content: string;
  graph_context: string[];
  metadata: Record<string, string | number | boolean | null>;
};

export type QueryPlan = {
  rewritten_query: string;
  modality_filter: string[];
  keywords: string[];
  top_k: number;
};

export type QueryResponse = {
  answer: string;
  query_plan: QueryPlan;
  retrieved_context: RetrievalResult[];
  graph_insights: string[];
  citations: string[];
};
