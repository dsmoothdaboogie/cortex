"""
query.py — Semantic retrieval pipeline
Queries local DB + any linked repo DBs, merges results by score.
"""

import chromadb
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from cortex.db import get_client, _project_name
from cortex.embed import embed_query

console = Console()


def _open_linked_collection(name: str):
    """Open a linked repo's ChromaDB collection. Returns None if not available."""
    db_path = Path.home() / ".cortex" / name / "chroma"
    if not db_path.exists():
        return None
    try:
        client = chromadb.PersistentClient(path=str(db_path))
        return client.get_collection("cortex")
    except Exception:
        return None


def _query_collection(col, vec, top_k: int, tag: str | None, project: str) -> list[dict]:
    """Query a single collection and return chunks tagged with their source project."""
    where = {"tag": tag} if tag else None
    count = col.count()
    if count == 0:
        return []
    try:
        results = col.query(
            query_embeddings=vec,
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
            **({"where": where} if where else {}),
        )
    except Exception:
        return []

    if not results["documents"][0]:
        return []

    return [
        {
            "text": doc.strip(),
            "source": meta.get("source", "unknown"),
            "score": round(1 - dist, 3),
            "chunk_index": meta.get("chunk_index", 0),
            "project": project,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def retrieve(query: str, top_k: int = 5, tag: str = None,
             context_only: bool = False, silent: bool = False) -> list[dict]:
    from cortex.config import load_linked

    # --- local DB ---
    client = get_client()
    local_project = _project_name()
    try:
        local_col = client.get_collection("cortex")
    except Exception:
        if not silent:
            console.print("[red]No DB found. Run: python3 cortex.py add <path>[/red]")
        return []

    vec = embed_query(query)
    all_chunks = _query_collection(local_col, vec, top_k, tag, local_project)

    # --- linked DBs ---
    linked = load_linked()
    skipped = []
    for entry in linked:
        name = entry["name"]
        allowed_tags = entry.get("tags")  # None = no filter, list = only these tags

        # If a specific tag is requested, only query linked repo if it allows that tag
        if tag and allowed_tags and tag not in allowed_tags:
            continue

        # Apply the linked repo's tag filter when querying (if no specific tag was requested)
        effective_tag = tag if tag else None
        if not tag and allowed_tags:
            # Query each allowed tag separately and merge — simpler: just query unfiltered
            # ChromaDB doesn't support OR filters, so query without tag filter and let
            # the semantic ranking do the work; the allowed_tags list is advisory for
            # cortex repos add --tags only, not enforced at query time unless a specific
            # --tag was passed by the caller.
            effective_tag = None

        col = _open_linked_collection(name)
        if col is None:
            skipped.append(name)
            continue

        chunks = _query_collection(col, vec, top_k, effective_tag, name)
        all_chunks.extend(chunks)

    # Merge, sort by score, take top_k
    all_chunks.sort(key=lambda c: c["score"], reverse=True)
    all_chunks = all_chunks[:top_k]

    if not all_chunks:
        if not silent:
            console.print("[yellow]No results found.[/yellow]")
        return []

    multi_repo = len(linked) > len(skipped) > 0 or (linked and not skipped)

    if context_only:
        lines = [f'## cortex context · "{query}"\n']
        if linked and not skipped:
            repos_queried = [local_project] + [e["name"] for e in linked if e["name"] not in skipped]
            lines.append(f"_Queried: {', '.join(repos_queried)}_\n")
        for i, c in enumerate(all_chunks):
            project_label = f" · [{c['project']}]" if multi_repo else ""
            lines.append(f"### [{i+1}] {c['source']}{project_label} · relevance: {c['score']}")
            lines.append(c["text"])
            lines.append("")
        print("\n".join(lines))
        return all_chunks

    if not silent:
        repos_label = ""
        if linked:
            queried = [local_project] + [e["name"] for e in linked if e["name"] not in skipped]
            repos_label = f"  [dim]({' + '.join(queried)})[/dim]"
        console.print(f"\n[cyan]cortex ask[/cyan] · [dim]\"{query}\"[/dim]{repos_label}\n")

        if skipped:
            console.print(f"[yellow]⚠ Linked repos not available locally:[/yellow] {', '.join(skipped)}\n")

        for c in all_chunks:
            color = "green" if c["score"] > 0.55 else "yellow" if c["score"] > 0.35 else "red"
            project_label = f"  [dim][{c['project']}][/dim]" if multi_repo else ""
            console.print(Panel(
                c["text"][:400] + ("..." if len(c["text"]) > 400 else ""),
                title=f"[{color}]{c['score']}[/{color}]  [dim]{c['source']}[/dim]{project_label}",
                border_style="dim", padding=(0, 1)
            ))

    return all_chunks


def format_context_block(chunks: list[dict], query: str = "") -> str:
    query_label = f' · "{query}"' if query else ""
    lines = [f"## Relevant Context (cortex){query_label}\n"]
    for i, c in enumerate(chunks):
        project_label = f" [{c['project']}]" if "project" in c else ""
        lines.append(f"### [{i+1}] {c['source']}{project_label} (relevance: {c['score']})")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)
