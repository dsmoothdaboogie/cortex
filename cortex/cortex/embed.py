"""
embed.py — Local embedding model singleton
Uses all-MiniLM-L6-v2 — no API key, ~90MB download on first run
"""

from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    return get_model().encode(texts, show_progress_bar=False).tolist()


def embed_query(text: str) -> list[list[float]]:
    return embed([text])
