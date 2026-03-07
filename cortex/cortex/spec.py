"""
spec.py — Spec sync, watch, and list
Spec files are source of truth — DB follows them.
"""

import re
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from cortex.db import get_client, get_or_create_collection
from cortex.ingest import ingest_file
from cortex.chunks import file_hash

console = Console()
SPECS_DIR = Path("cortex/specs")
KNOWLEDGE_DIR = Path("cortex/knowledge")

KNOWLEDGE_TAG_MAP: dict[str, str] = {
    "standards":        "standards",
    "design-system":    "design-system",
    "adrs":             "adr",
    "vision":           "vision",
    "skills":           "skills",
    "patterns":         "patterns",
    "team-conventions": "team-conventions",
}


def get_stored_hash(source: str, collection) -> Optional[str]:
    try:
        r = collection.get(where={"source": source}, include=["metadatas"])
        if r["metadatas"]:
            return r["metadatas"][0].get("file_hash")
    except Exception:
        pass
    return None


def get_all_specs() -> list[Path]:
    if not SPECS_DIR.exists():
        return []
    return sorted(SPECS_DIR.glob("*.md"))


def get_all_knowledge_files() -> list[tuple[Path, str]]:
    """Return (path, tag) pairs for all knowledge markdown files."""
    result = []
    for folder, tag in KNOWLEDGE_TAG_MAP.items():
        folder_path = KNOWLEDGE_DIR / folder
        if folder_path.exists():
            for f in sorted(folder_path.rglob("*.md")):
                result.append((f, tag))
    return result


def is_stale(spec_path: Path, collection) -> bool:
    stored = get_stored_hash(str(spec_path), collection)
    if stored is None:
        return True
    return stored != file_hash(str(spec_path))


def cmd_sync(verbose: bool = False) -> int:
    specs = get_all_specs()
    if not specs:
        console.print("[yellow]No specs found in specs/[/yellow]")
        return 0

    client = get_client()
    col = get_or_create_collection(client)
    stale = [s for s in specs if is_stale(s, col)]

    if not stale:
        console.print("[green]✓[/green] All specs are up to date.")
        return 0

    console.print(f"\n[cyan]cortex sync[/cyan] · {len(stale)} spec(s) to sync\n")
    synced = 0
    for s in stale:
        n = ingest_file(s, col, tag="spec", force=True, silent=not verbose)
        if n > 0:
            synced += 1
            if not verbose:
                console.print(f"  [green]✓[/green] {s}")

    console.print(f"\n[green]Done.[/green] {synced} spec(s) synced.\n")
    return synced


def cmd_sync_check() -> list[Path]:
    specs = get_all_specs()
    if not specs:
        return []
    client = get_client()
    col = get_or_create_collection(client)
    return [s for s in specs if is_stale(s, col)]


def cmd_sync_knowledge(verbose: bool = False, quiet: bool = False) -> int:
    """Sync changed knowledge/ files to DB."""
    files = get_all_knowledge_files()
    if not files:
        if not quiet:
            console.print("[yellow]No knowledge files found in knowledge/[/yellow]")
        return 0

    client = get_client()
    col = get_or_create_collection(client)
    stale = [(f, t) for f, t in files if is_stale(f, col)]

    if not stale:
        if not quiet:
            console.print("[green]✓[/green] All knowledge files are up to date.")
        return 0

    if not quiet:
        console.print(f"\n[cyan]cortex sync --knowledge[/cyan] · {len(stale)} file(s) to sync\n")

    synced = 0
    for f, t in stale:
        n = ingest_file(f, col, tag=t, force=True, silent=not verbose)
        if n > 0:
            synced += 1
            if not quiet and not verbose:
                console.print(f"  [green]✓[/green] [{t}] {f}")

    if not quiet:
        console.print(f"\n[green]Done.[/green] {synced} file(s) synced.\n")
    return synced


def cmd_watch(interval: float = 1.0, knowledge: bool = False):
    SPECS_DIR.mkdir(exist_ok=True)
    what = "specs/ + knowledge/" if knowledge else "specs/"
    console.print(f"\n[cyan]cortex watch[/cyan] · watching [yellow]{what}[/yellow]\n")
    console.print("[dim]Auto-syncing on save. Ctrl+C to stop.[/dim]\n")

    client = get_client()
    col = get_or_create_collection(client)
    last: dict[str, str] = {str(s): file_hash(str(s)) for s in get_all_specs()}

    if knowledge:
        for f, _ in get_all_knowledge_files():
            last[str(f)] = file_hash(str(f))

    try:
        while True:
            time.sleep(interval)
            for spec in get_all_specs():
                key = str(spec)
                try:
                    current = file_hash(key)
                except Exception:
                    continue
                if last.get(key) != current:
                    last[key] = current
                    n = ingest_file(spec, col, tag="spec", force=True, silent=True)
                    if n > 0:
                        from datetime import datetime
                        ts = datetime.now().strftime("%H:%M:%S")
                        console.print(f"  [dim]{ts}[/dim] [green]synced[/green] [yellow]spec[/yellow]     {spec}")

            if knowledge:
                for f, tag in get_all_knowledge_files():
                    key = str(f)
                    try:
                        current = file_hash(key)
                    except Exception:
                        continue
                    if last.get(key) != current:
                        last[key] = current
                        n = ingest_file(f, col, tag=tag, force=True, silent=True)
                        if n > 0:
                            from datetime import datetime
                            ts = datetime.now().strftime("%H:%M:%S")
                            console.print(f"  [dim]{ts}[/dim] [green]synced[/green] [yellow]{tag:<12}[/yellow] {f}")
    except KeyboardInterrupt:
        console.print("\n[dim]Watch stopped.[/dim]\n")


def cmd_list():
    specs = get_all_specs()
    if not specs:
        console.print("[yellow]No specs found in specs/[/yellow]")
        return

    client = get_client()
    col = get_or_create_collection(client)
    pattern = re.compile(r"^([A-Z]+-\d+)-(\d{4}-\d{2}-\d{2})-(.+)\.md$")

    table = Table(title="[cyan]cortex specs[/cyan]")
    table.add_column("File", style="dim")
    table.add_column("Ticket", style="yellow")
    table.add_column("Date", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("DB Sync", justify="center")

    for s in specs:
        m = pattern.match(s.name)
        ticket = m.group(1) if m else "—"
        date = m.group(2) if m else "—"
        status = "Draft"
        try:
            sm = re.search(r"\*\*Status:\*\*\s*(.+)", s.read_text())
            if sm:
                status = sm.group(1).strip()
        except Exception:
            pass
        stale = is_stale(s, col)
        sync = "[yellow]stale[/yellow]" if stale else "[green]✓[/green]"
        color = {"Draft": "dim", "In Progress": "yellow",
                 "Review": "cyan", "Done": "green"}.get(status, "dim")
        table.add_row(s.name, ticket, date, f"[{color}]{status}[/{color}]", sync)

    console.print()
    console.print(table)
    console.print()
