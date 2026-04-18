from __future__ import annotations

import math
import re
from collections import Counter
from hashlib import md5


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    normalized = normalize_whitespace(text)
    if not normalized:
        return []

    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    text_length = len(normalized)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = normalized[start:end]
        if end < text_length:
            last_period = chunk.rfind(". ")
            last_space = chunk.rfind(" ")
            split_at = last_period if last_period > chunk_size * 0.55 else last_space
            if split_at > 0:
                end = start + split_at + 1
                chunk = normalized[start:end]
        chunks.append(chunk.strip())
        if end >= text_length:
            break
        start = max(end - overlap, start + 1)
    return chunks


def extract_entities(text: str, limit: int = 10) -> list[str]:
    email_matches = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    url_matches = re.findall(r"https?://[^\s]+", text)
    proper_nouns = re.findall(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b", text)

    entity_counter = Counter()
    for entity in email_matches + url_matches + proper_nouns:
        normalized = normalize_whitespace(entity)
        if len(normalized) > 2:
            entity_counter[normalized] += 1

    return [entity for entity, _ in entity_counter.most_common(limit)]


def extract_keywords(text: str, limit: int = 8) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", text.lower())
    counter = Counter(token for token in tokens if token not in STOPWORDS)
    return [token for token, _ in counter.most_common(limit)]


def hashed_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}", text.lower())
    if not tokens:
        return vector

    for token in tokens:
        digest = md5(token.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % dimensions
        sign = -1.0 if int(digest[8:10], 16) % 2 else 1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector

    return [value / norm for value in vector]
