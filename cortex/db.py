"""
db.py — ChromaDB persistent client
Data stored at ~/.cortex/{project-name}/chroma (one DB per repo)
"""

import subprocess
import chromadb
from pathlib import Path


def _project_name() -> str:
    """Derive project name from git root name, falling back to CWD name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip()).name
    except Exception:
        pass
    return Path.cwd().name


def _cortex_dir() -> Path:
    return Path.home() / ".cortex" / _project_name() / "chroma"


def get_client() -> chromadb.PersistentClient:
    cortex_dir = _cortex_dir()
    cortex_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(cortex_dir))


def get_or_create_collection(client, name: str = "cortex"):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
