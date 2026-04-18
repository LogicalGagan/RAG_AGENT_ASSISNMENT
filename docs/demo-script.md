# 10-Minute Demo Script

## 1. Introduction

Say that this is a **full-stack multi-modal Graph RAG system** that supports:

- text
- PDFs
- images

and combines:

- vector retrieval using ChromaDB
- graph reasoning using NetworkX
- local Ollama generation for grounded answers

## 2. Architecture Overview

Show the Mermaid diagram from the README and explain the pipeline in one line each:

- ingestion API receives files
- modality-specific extraction converts them to retrieval-ready text
- chunks are stored in ChromaDB
- entities and relationships are stored in the knowledge graph
- user query triggers retrieval + graph expansion + answer generation

## 3. Ingestion Demo

Upload:

- one `.txt` file
- one `.pdf`
- one `.jpeg` or `.png`

While doing that, say:

- text and PDF are parsed directly
- images are described using local Ollama vision
- all modalities are normalized into searchable text before retrieval

Then highlight in the UI:

- inventory cards
- file counts
- chunk counts
- entity counts
- graph node and edge totals

## 4. Query Demo

Ask a cross-modal question such as:

`Summarize the uploaded knowledge base and mention what the image shows.`

Then point out:

- the answer panel
- citations
- graph insights
- retrieved evidence cards

Mention that the answer is grounded in retrieved context instead of direct free-form generation.

## 5. Inventory Management Demo

Remove one uploaded file from the inventory using the `Remove File` button.

Then show:

- the card disappears
- the graph metrics update
- the removed file no longer affects later answers

This helps demonstrate lifecycle management, not just ingestion.

## 6. Engineering Choices

Briefly explain:

- `ChromaDB` was chosen for simple local vector persistence
- `NetworkX` was chosen for lightweight graph reasoning without extra operational overhead
- `qwen2:0.5b` was chosen for lightweight local answer generation
- `moondream` was chosen for local image understanding
- local Ollama was used to avoid cloud quota issues during live demo

## 7. Close

Finish by connecting the design to the literature survey:

- modern agentic systems rely on memory, planning, and tool orchestration
- this project applies that idea through vector retrieval, graph memory, and orchestrated grounded generation
