from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from PIL import Image
from PyPDF2 import PdfReader

from ..config import Settings
from ..utils.text import chunk_text, extract_entities, normalize_whitespace
from .llm import LLMService


TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".html", ".htm"}
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}


@dataclass
class ChunkPayload:
    chunk_id: str
    document_id: str
    title: str
    modality: str
    content: str
    metadata: dict


@dataclass
class ProcessedDocument:
    document_id: str
    filename: str
    title: str
    modality: str
    raw_text: str
    chunks: list[ChunkPayload]
    entities: list[str]
    metadata: dict

    def to_registry_record(self) -> dict:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "title": self.title,
            "modality": self.modality,
            "chunk_count": len(self.chunks),
            "entity_count": len(self.entities),
            "created_at": self.metadata["created_at"],
            "metadata": self.metadata,
        }


class ModalityProcessor:
    def __init__(self, settings: Settings, llm_service: LLMService) -> None:
        self.settings = settings
        self.llm_service = llm_service

    def detect_modality(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in PDF_EXTENSIONS:
            return "pdf"
        if suffix in IMAGE_EXTENSIONS:
            return "image"
        if suffix in AUDIO_EXTENSIONS:
            return "audio"
        if suffix in TEXT_EXTENSIONS:
            return "text"
        return "text"

    def process(self, file_path: Path, original_filename: str | None = None) -> ProcessedDocument:
        modality = self.detect_modality(file_path)
        document_id = str(uuid4())
        display_name = original_filename or file_path.name
        title = Path(display_name).stem.replace("_", " ").replace("-", " ").title()

        if modality == "pdf":
            raw_text, metadata = self._extract_pdf(file_path)
        elif modality == "image":
            raw_text, metadata = self._extract_image(file_path)
        elif modality == "audio":
            raw_text, metadata = self._extract_audio(file_path)
        else:
            raw_text, metadata = self._extract_text(file_path)

        raw_text = normalize_whitespace(raw_text)
        metadata["source_path"] = str(file_path)
        chunks = self._build_chunks(document_id, title, modality, raw_text, metadata)
        entities = extract_entities(raw_text)

        return ProcessedDocument(
            document_id=document_id,
            filename=display_name,
            title=title,
            modality=modality,
            raw_text=raw_text,
            chunks=chunks,
            entities=entities,
            metadata=metadata,
        )

    def _extract_text(self, file_path: Path) -> tuple[str, dict]:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return text, {"extension": file_path.suffix.lower()}

    def _extract_pdf(self, file_path: Path) -> tuple[str, dict]:
        reader = PdfReader(str(file_path))
        pages: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            pages.append(f"Page {index}: {page_text}")
        return " ".join(pages), {"extension": file_path.suffix.lower(), "page_count": len(reader.pages)}

    def _extract_image(self, file_path: Path) -> tuple[str, dict]:
        with Image.open(file_path) as image:
            width, height = image.size
            mode = image.mode

        description = self.llm_service.describe_image(file_path, file_path.name)
        if not description:
            description = (
                f"Image file named {file_path.stem}. "
                f"It has dimensions {width}x{height} pixels and color mode {mode}. "
                "No external vision model was configured, so this fallback summary is based on file metadata."
            )

        return description, {"extension": file_path.suffix.lower(), "width": width, "height": height, "color_mode": mode}

    def _extract_audio(self, file_path: Path) -> tuple[str, dict]:
        transcript = self.llm_service.transcribe_audio(file_path)
        if not transcript:
            transcript = (
                f"Audio file named {file_path.stem}. "
                "No transcription provider was configured, so only filename-level metadata is available."
            )
        return transcript, {"extension": file_path.suffix.lower()}

    def _build_chunks(
        self,
        document_id: str,
        title: str,
        modality: str,
        raw_text: str,
        metadata: dict,
    ) -> list[ChunkPayload]:
        fallback_text = raw_text or "No extractable textual content was available for this file."
        raw_chunks = chunk_text(fallback_text, self.settings.chunk_size, self.settings.chunk_overlap) or [fallback_text]
        chunk_payloads: list[ChunkPayload] = []
        for index, chunk in enumerate(raw_chunks, start=1):
            chunk_payloads.append(
                ChunkPayload(
                    chunk_id=f"{document_id}-chunk-{index}",
                    document_id=document_id,
                    title=title,
                    modality=modality,
                    content=chunk,
                    metadata={**metadata, "chunk_index": index},
                )
            )
        return chunk_payloads
