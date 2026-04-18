from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import networkx as nx
from networkx.readwrite import json_graph

from ..config import Settings
from ..utils.text import extract_entities
from .modality import ProcessedDocument


class GraphStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.path = Path(settings.graph_path)
        self.graph = self._load_graph()

    def _load_graph(self) -> nx.MultiDiGraph:
        if self.path.exists():
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return json_graph.node_link_graph(payload, directed=True, multigraph=True)
        return nx.MultiDiGraph()

    def _save(self) -> None:
        payload = json_graph.node_link_data(self.graph)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add_document(self, document: ProcessedDocument) -> None:
        doc_node = f"doc::{document.document_id}"
        self.graph.add_node(
            doc_node,
            kind="document",
            title=document.title,
            modality=document.modality,
            filename=document.filename,
        )

        for chunk in document.chunks:
            chunk_node = f"chunk::{chunk.chunk_id}"
            chunk_entities = extract_entities(chunk.content, limit=6) or document.entities
            self.graph.add_node(
                chunk_node,
                kind="chunk",
                modality=chunk.modality,
                title=chunk.title,
                preview=chunk.content[:240],
            )
            self.graph.add_edge(doc_node, chunk_node, relation="HAS_CHUNK")

            for entity in set(chunk_entities):
                entity_node = f"entity::{entity}"
                mention_count = self.graph.nodes[entity_node]["mention_count"] if entity_node in self.graph else 0
                self.graph.add_node(entity_node, kind="entity", value=entity, mention_count=mention_count + 1)
                self.graph.add_edge(chunk_node, entity_node, relation="MENTIONS")
                self.graph.add_edge(doc_node, entity_node, relation="CONTAINS_ENTITY")

                related_docs = [
                    neighbor
                    for neighbor in self.graph.predecessors(entity_node)
                    if neighbor.startswith("doc::") and neighbor != doc_node
                ]
                for related_doc in related_docs:
                    related_modality = self.graph.nodes[related_doc].get("modality")
                    if related_modality != document.modality:
                        self.graph.add_edge(doc_node, related_doc, relation="CROSS_MODAL_LINK", entity=entity)

        self._save()

    def expand_hit(self, document_id: str, chunk_id: str, limit: int) -> list[str]:
        doc_node = f"doc::{document_id}"
        chunk_node = f"chunk::{chunk_id}"
        insights: list[str] = []

        for node in (chunk_node, doc_node):
            if node not in self.graph:
                continue
            for neighbor in list(self.graph.neighbors(node))[:limit]:
                edge_data = self.graph.get_edge_data(node, neighbor)
                if not edge_data:
                    continue
                relation = next(iter(edge_data.values())).get("relation", "RELATED")
                neighbor_data = self.graph.nodes[neighbor]
                if neighbor_data.get("kind") == "entity":
                    insights.append(f"{relation}: {neighbor_data.get('value')}")
                elif neighbor_data.get("kind") == "chunk":
                    insights.append(f"{relation}: related chunk from {neighbor_data.get('title')}")
                elif neighbor_data.get("kind") == "document":
                    insights.append(
                        f"{relation}: {neighbor_data.get('title')} ({neighbor_data.get('modality')})"
                    )
        return insights[:limit]

    def summarize(self) -> dict:
        modality_counter = Counter()
        entity_counter = Counter()

        for _, data in self.graph.nodes(data=True):
            if data.get("kind") == "document":
                modality_counter[data.get("modality", "unknown")] += 1
            if data.get("kind") == "entity":
                entity_counter[data.get("value", "")] += int(data.get("mention_count", 1))

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "documents_by_modality": dict(modality_counter),
            "top_entities": [entity for entity, _ in entity_counter.most_common(8) if entity],
        }
