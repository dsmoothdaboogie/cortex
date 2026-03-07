"""
ingest.py — File ingestion pipeline
Chunks, embeds, and stores documents in ChromaDB
"""

from pathlib import Path
from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from cortex.db import get_client, get_or_create_collection
from cortex.embed import embed
from cortex.chunks import chunk_text, file_hash

console = Console()

SUPPORTED = {
    ".md", ".txt", ".ts", ".tsx", ".js", ".jsx",
    ".py", ".json", ".yaml", ".yml", ".html", ".css", ".scss"
}


def collect_files(paths: List[str]) -> List[Path]:
    files = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            if path.suffix in SUPPORTED:
                files.append(path)
        elif path.is_dir():
            for f in path.glob("**/*"):
                if f.is_file() and f.suffix in SUPPORTED:
                    files.append(f)
        else:
            console.print(f"[red]Not found:[/red] {p}")
    return sorted(set(files))


def ingest_file(file_path: Path, collection, tag: str = None,
                force: bool = False, silent: bool = False) -> int:
    rel = str(file_path)
    fhash = file_hash(rel)

    if not force:
        existing = collection.get(where={"source": rel}, include=["metadatas"])
        if existing["metadatas"] and existing["metadatas"][0].get("file_hash") == fhash:
            if not silent:
                console.print(f"  [dim]skipped (unchanged):[/dim] {rel}")
            return 0

    try:
        collection.delete(where={"source": rel})
    except Exception:
        pass

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_text(text)
    if not chunks:
        return 0

    embeddings = embed(chunks)
    ids = [f"{fhash}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": rel, "chunk_index": i, "file_hash": fhash,
         "extension": file_path.suffix,
         **({"tag": tag} if tag else {})}
        for i in range(len(chunks))
    ]

    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

    if not silent:
        console.print(f"  [green]✓[/green] {rel} [dim]→ {len(chunks)} chunks[/dim]")
    return len(chunks)


def ingest_paths(paths: List[str], tag: str = None, force: bool = False) -> dict:
    files = collect_files(paths)
    if not files:
        console.print("[red]No supported files found.[/red]")
        return {"files": 0, "chunks": 0, "skipped": 0}

    console.print(f"\n[cyan]cortex add[/cyan] · {len(files)} file(s)\n")

    client = get_client()
    col = get_or_create_collection(client)
    total, skipped = 0, 0

    with Progress(SpinnerColumn(), TextColumn("{task.description}"),
                  BarColumn(), TaskProgressColumn(),
                  console=console, transient=True) as p:
        task = p.add_task("Ingesting...", total=len(files))
        for f in files:
            n = ingest_file(f, col, tag=tag, force=force)
            if n == 0:
                skipped += 1
            else:
                total += n
            p.advance(task)

    console.print(
        f"\n[green]Done.[/green] [yellow]{total}[/yellow] chunks · "
        f"[dim]{skipped} skipped[/dim]\n"
    )
    return {"files": len(files) - skipped, "chunks": total, "skipped": skipped}
