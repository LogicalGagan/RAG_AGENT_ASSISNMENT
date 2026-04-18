import { useState, type FormEvent } from "react";

import { queryKnowledgeBase } from "../lib";
import type { QueryResponse } from "../types";

const modalities = ["text", "pdf", "image", "audio"];
const promptSuggestions = [
  "Summarize the uploaded knowledge base.",
  "Compare the PDF content with the uploaded image.",
  "What are the main entities mentioned across the files?",
];

type QueryWorkspaceProps = {
  onResult: (result: QueryResponse | null) => void;
};

export function QueryWorkspace({ onResult }: QueryWorkspaceProps) {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [selectedModalities, setSelectedModalities] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await queryKnowledgeBase({
        question,
        top_k: topK,
        selected_modalities: selectedModalities,
      });
      onResult(result);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Query failed.");
    } finally {
      setLoading(false);
    }
  }

  function toggleModality(modality: string) {
    setSelectedModalities((current) =>
      current.includes(modality) ? current.filter((item) => item !== modality) : [...current, modality],
    );
  }

  return (
    <section className="glass-card panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Query Console</p>
          <h2>Ask grounded questions</h2>
        </div>
      </div>
      <form className="query-form" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Example: Compare what the PDF says about the architecture with what the uploaded image illustrates."
          rows={5}
          required
        />
        <div className="suggestion-row">
          {promptSuggestions.map((suggestion) => (
            <button key={suggestion} type="button" className="suggestion-chip" onClick={() => setQuestion(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>
        <div className="controls-row">
          <label className="field">
            <span>Top-K retrieval</span>
            <input
              type="number"
              min={1}
              max={10}
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
            />
          </label>
          <div className="field">
            <span>Modalities</span>
            <div className="tag-row">
              {modalities.map((modality) => (
                <button
                  key={modality}
                  type="button"
                  className={`filter-chip ${selectedModalities.includes(modality) ? "active" : ""}`}
                  onClick={() => toggleModality(modality)}
                >
                  {modality}
                </button>
              ))}
            </div>
          </div>
        </div>
        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? "Retrieving grounded answer..." : "Run Graph RAG Query"}
        </button>
        {error ? <p className="error-text">{error}</p> : null}
      </form>
    </section>
  );
}
