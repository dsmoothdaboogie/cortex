"""
embed.py — Lexical embedding via scikit-learn (no model download required)

Uses HashingVectorizer + SparseRandomProjection to produce 384-dim dense vectors.
Deterministic and stateless — no fitting, no external files.
"""

from __future__ import annotations
import numpy as np

_vectorizer = None
_projection = None


def _init():
    global _vectorizer, _projection
    if _vectorizer is not None:
        return

    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.random_projection import SparseRandomProjection
    import scipy.sparse as sp

    _vectorizer = HashingVectorizer(n_features=2**16, norm="l2", alternate_sign=False)
    _projection = SparseRandomProjection(n_components=384, random_state=42)
    # random_state=42 means the projection matrix is always identical — stateless
    _projection.fit(sp.eye(1, 2**16))


def embed(texts: list[str]) -> list[list[float]]:
    _init()
    sparse = _vectorizer.transform(texts)
    dense = np.array(_projection.transform(sparse.toarray()), dtype=np.float32)
    return dense.tolist()


def embed_query(text: str) -> list[list[float]]:
    return embed([text])


def get_model():
    """Legacy shim — returns None (no transformer model used)."""
    return None
