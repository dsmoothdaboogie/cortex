"""
chunks.py — Text chunking and file hashing
"""

import hashlib
from typing import List


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """Split text into overlapping character-based chunks at word boundaries.

    chunk_size and overlap are in characters.
    1500 chars ≈ 300 words — safely within all-MiniLM-L6-v2's 256 subword token limit.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Extend to the next word boundary so we don't cut mid-word
        if end < text_len:
            while end < text_len and not text[end].isspace():
                end += 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        # Rewind by overlap, then step forward to the next word boundary
        start = end - overlap
        while start < end and not text[start].isspace():
            start += 1
        start = max(start, end - overlap)

    return chunks


def file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
