from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DocumentRegistry:
    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self.registry_path.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict[str, Any]]:
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def _write(self, data: list[dict[str, Any]]) -> None:
        self.registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def list_documents(self) -> list[dict[str, Any]]:
        return sorted(self._read(), key=lambda item: item["created_at"], reverse=True)

    def upsert_document(self, document: dict[str, Any]) -> None:
        documents = self._read()
        replaced = False
        for index, existing in enumerate(documents):
            if existing["document_id"] == document["document_id"]:
                documents[index] = document
                replaced = True
                break
        if not replaced:
            documents.append(document)
        self._write(documents)

    def delete_document(self, document_id: str) -> dict[str, Any] | None:
        documents = self._read()
        remaining: list[dict[str, Any]] = []
        deleted: dict[str, Any] | None = None

        for document in documents:
            if document["document_id"] == document_id:
                deleted = document
                continue
            remaining.append(document)

        if deleted is not None:
            self._write(remaining)
        return deleted
