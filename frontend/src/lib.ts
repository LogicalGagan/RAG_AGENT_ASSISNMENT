import type { DocumentSummary, GraphSummary, QueryResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed.");
  }
  return (await response.json()) as T;
}

export async function fetchDocuments(): Promise<DocumentSummary[]> {
  const response = await fetch(`${API_BASE}/documents`);
  return parseResponse<DocumentSummary[]>(response);
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
  });
  await parseResponse(response);
}

export async function fetchGraphSummary(): Promise<GraphSummary> {
  const response = await fetch(`${API_BASE}/graph`);
  return parseResponse<GraphSummary>(response);
}

export async function uploadFiles(files: File[]): Promise<void> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const response = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    body: formData,
  });

  await parseResponse(response);
}

export async function queryKnowledgeBase(payload: {
  question: string;
  top_k: number;
  selected_modalities: string[];
}): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseResponse<QueryResponse>(response);
}
