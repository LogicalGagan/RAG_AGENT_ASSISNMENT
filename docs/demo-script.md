# 10-Minute Demo Script

## 1. Problem Statement

Explain that the goal is not just document Q&A, but multi-modal grounded retrieval across text, PDFs, and images with graph-aware reasoning.

## 2. Architecture

Show the Mermaid diagram in the README and explain:

- ingestion layer
- vector retrieval layer
- graph layer
- generation layer

## 3. Ingestion Demo

Upload:

- one `.txt` or `.md` file
- one `.pdf`
- one `.jpeg` or `.png`

Then highlight:

- indexed file cards
- chunk counts
- entity counts
- graph node and edge totals

## 4. Query Demo

Ask a question that requires cross-modal grounding, for example:

`Compare what the document explains about the system architecture with what the uploaded image suggests.`

Point out:

- rewritten query
- retrieved evidence
- graph insights
- final grounded answer

## 5. Engineering Discussion

Briefly explain:

- why ChromaDB was chosen for simplicity
- why NetworkX was chosen over Neo4j for a lightweight demo
- why the app includes offline fallbacks for reliability

## 6. Close

End with the literature survey and note that the design is inspired by agent architectures that combine planning, memory, and tool use.
