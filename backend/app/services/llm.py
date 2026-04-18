from __future__ import annotations

import base64
from pathlib import Path

from ..config import Settings
from ..schemas import QueryPlan, RetrievalResult

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency path
    OpenAI = None


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.use_openai and OpenAI else None

    def generate_answer(
        self,
        question: str,
        query_plan: QueryPlan,
        retrieved_context: list[RetrievalResult],
        graph_insights: list[str],
    ) -> str:
        if not retrieved_context:
            return "I could not find relevant evidence in the indexed knowledge base yet. Please ingest more files and try again."

        if self.client:
            prompt = self._build_answer_prompt(question, query_plan, retrieved_context, graph_insights)
            response = self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise RAG assistant. Answer only from the supplied context, cite evidence naturally, and mention uncertainty when context is incomplete.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""

        summary_lines = [
            f"Question: {question}",
            "",
            "Answer synthesized from retrieved context:",
        ]
        for item in retrieved_context[:3]:
            summary_lines.append(f"- {item.title} ({item.modality}): {item.content[:260].strip()}")
        if graph_insights:
            summary_lines.append("")
            summary_lines.append("Graph insights:")
            for insight in graph_insights[:3]:
                summary_lines.append(f"- {insight}")
        return "\n".join(summary_lines)

    def describe_image(self, image_path: Path, filename: str) -> str:
        if not self.client:
            return ""

        encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        suffix = image_path.suffix.lower().replace(".", "") or "jpeg"
        data_url = f"data:image/{suffix};base64,{encoded}"
        response = self.client.chat.completions.create(
            model=self.settings.openai_chat_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Describe the key semantic content of this image named {filename} for retrieval in a RAG system. Keep it to 5-7 sentences."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def transcribe_audio(self, audio_path: Path) -> str:
        if not self.client:
            return ""

        with audio_path.open("rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return getattr(transcript, "text", "") or ""

    def _build_answer_prompt(
        self,
        question: str,
        query_plan: QueryPlan,
        retrieved_context: list[RetrievalResult],
        graph_insights: list[str],
    ) -> str:
        context_blocks: list[str] = []
        for item in retrieved_context:
            graph_text = " | ".join(item.graph_context) if item.graph_context else "No graph neighbors"
            context_blocks.append(
                f"[{item.title} | {item.modality} | score={item.score:.3f}]\n"
                f"Content: {item.content}\n"
                f"Graph: {graph_text}"
            )
        graph_block = "\n".join(f"- {insight}" for insight in graph_insights) or "- No additional graph insights"
        return (
            f"User question: {question}\n"
            f"Rewritten query: {query_plan.rewritten_query}\n"
            f"Keywords: {', '.join(query_plan.keywords)}\n\n"
            f"Retrieved context:\n\n{'\n\n'.join(context_blocks)}\n\n"
            f"Graph-level insights:\n{graph_block}\n\n"
            "Produce a concise answer with evidence-backed reasoning and mention which modalities contributed."
        )
