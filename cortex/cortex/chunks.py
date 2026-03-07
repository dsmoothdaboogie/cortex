"""
chunks.py — Text chunking and file hashing
"""

import hashlib
from typing import List
import tiktoken


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
