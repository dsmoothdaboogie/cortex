"""
embed.py — Local embedding with scikit-learn fallback

Primary:  all-MiniLM-L6-v2 via sentence-transformers (local cache only — no download)
Fallback: HashingVectorizer + SparseRandomProjection from scikit-learn (zero downloads)
          Used automatically when the transformer model is not cached locally.
"""

from __future__ import annotations
import os
import numpy as np

_model = None        # SentenceTransformer instance (primary)
_vectorizer = None   # HashingVectorizer (fallback)
_projection = None   # SparseRandomProjection (fallback)
_using_fallback: bool | None = None  # None = not yet initialised


def _init():
    global _model, _vectorizer, _projection, _using_fallback
    if _using_fallback is not None:
        return  # already initialised

    # ── Primary: sentence-transformers (local cache only) ───────────────────
    try:
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        _using_fallback = False
        return
    except Exception:
        pass

    # ── Fallback: scikit-learn (no downloads, deterministic) ────────────────
    import warnings
    warnings.warn(
        "\n[cortex] sentence-transformers model not found locally.\n"
        "  Falling back to TF-IDF + random projection (keyword-based search).\n"
        "  To restore semantic search: download all-MiniLM-L6-v2 to this machine.\n",
        stacklevel=2,
    )
    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.random_projection import SparseRandomProjection
    import scipy.sparse as sp

    _vectorizer = HashingVectorizer(n_features=2**16, norm="l2", alternate_sign=False)
    _projection = SparseRandomProjection(n_components=384, random_state=42)
    # Fit projection on a dummy sample — random_state=42 means the matrix is
    # always identical regardless of data, so this is effectively stateless.
    _projection.fit(sp.eye(1, 2**16))
    _using_fallback = True


def embed(texts: list[str]) -> list[list[float]]:
    _init()
    if not _using_fallback:
        return _model.encode(texts, show_progress_bar=False).tolist()

    sparse = _vectorizer.transform(texts)
    dense = np.array(_projection.transform(sparse.toarray()), dtype=np.float32)
    return dense.tolist()


def embed_query(text: str) -> list[list[float]]:
    return embed([text])


def get_model():
    """Legacy shim — callers that need the raw SentenceTransformer still work."""
    _init()
    return _model  # may be None if using fallback
