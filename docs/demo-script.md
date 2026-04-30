# 10-Minute Demo Script

## 1. Introduction

Say that this is a **full-stack multi-modal Graph RAG system** that supports:

- text
- PDFs
- images

and combines:

- vector retrieval using Pinecone
- graph reasoning using NetworkX
- local Ollama generation for grounded answers

## 2. Architecture Overview

Show the Mermaid diagram from the README and explain the pipeline in one line each:

- ingestion API receives files
- modality-specific extraction converts them to retrieval-ready text
- chunks are stored in Pinecone and images are embedded directly with CLIP
- entities and relationships are stored in the knowledge graph
- user query triggers retrieval + graph expansion + answer generation

## 3. Ingestion Demo

Upload:

- one `.txt` file
- one `.pdf`
- one `.jpeg` or `.png`

While doing that, say:

- text and PDF are parsed directly
- images are directly embedded using a CLIP visual model
- text descriptions are embedded using the same CLIP model, putting everything in the same search space

Then highlight in the UI:

- inventory cards
- file counts
- chunk counts
- entity counts
- graph node and edge totals

## 4. Query Demo

Ask a cross-modal question such as:

`Find me running shoes that look like this uploaded image, and summarize their reviews.`

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

- `Pinecone` was chosen for serverless cloud vector storage to save local RAM
- `NetworkX` was chosen for lightweight graph reasoning without extra operational overhead
- `qwen2:0.5b` was chosen for lightweight local answer generation
- `sentence-transformers/clip-ViT-B-32` was chosen to demonstrate true cross-modal vector embedding
- local Ollama was used to avoid cloud quota issues during live demo

## 7. Close

Finish by connecting the design to the literature survey:

- modern agentic systems rely on memory, planning, and tool orchestration
- this project applies that idea through vector retrieval, graph memory, and orchestrated grounded generation
