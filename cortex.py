#!/usr/bin/env python3
"""
cortex — local knowledge base CLI for spec-driven development

Data pipeline commands:
  add <paths>          Ingest files or folders into the DB
  ask <query>          Search the knowledge base (includes linked repos)
  sync                 Sync changed specs (or knowledge/ with --knowledge) to DB
  watch                Auto-sync specs on file save (add --knowledge for knowledge/)
  audit                Show knowledge tag coverage — flag empty or sparse tags
  ls                   List indexed documents or specs
  stats                Show DB statistics
  rm <source>          Remove a source from the DB
  generate <artifact>  Regenerate standards / vision / adr artifact

Cross-repo commands:
  repos add <name>     Link another repo's DB to this project's queries
  repos rm <name>      Remove a linked repo
  repos ls             List linked repos and their local DB status
  repos sync           Re-ingest knowledge from all linked repos with known local paths

Setup commands:
  init                 Create cortex folder structure in current repo
  bootstrap            Get fully operational after cloning an existing cortex repo
  reset                Delete the local ChromaDB (all chunks removed)
  install-hook         Install git pre-commit + post-merge hooks
  uninstall-hook       Remove cortex git hooks
  hook-run             Called internally by the pre-commit hook
"""

import sys
import os
from pathlib import Path

# ── auto-relaunch with venv python if needed ───────────────────────────────────
_HERE = Path(__file__).parent
_VENV_PYTHON = _HERE / "cortex" / ".venv" / "bin" / "python"
if _VENV_PYTHON.exists() and sys.prefix != str(_VENV_PYTHON.parent.parent):
    os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON)] + sys.argv)
# ──────────────────────────────────────────────────────────────────────────────

# The cortex Python package lives at cortex/cortex/ — add cortex/ to sys.path
sys.path.insert(0, str(_HERE / "cortex"))

import click
from rich.console import Console

console = Console()


@click.group()
def cli():
    """cortex — knowledge base for spec-driven development."""
    pass


# ─── ADD ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("paths", nargs=-1, required=True)
@click.option("--tag", "-t", default=None,
              help="Tag: standards | design-system | adr | vision | skills | patterns | team-conventions | spec")
@click.option("--force", "-f", is_flag=True, help="Re-ingest even if file unchanged")
def add(paths, tag, force):
    """Ingest files or directories into the knowledge base.

    \b
    Examples:
      python3 cortex.py add ./knowledge/standards --tag standards
      python3 cortex.py add ./knowledge/design-system --tag design-system
      python3 cortex.py add ./knowledge/adrs --tag adr --force
      python3 cortex.py add ./specs --tag spec
    """
    from cortex.ingest import ingest_paths
    ingest_paths(list(paths), tag=tag, force=force)


# ─── ASK ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("query")
@click.option("--top-k", "-k", default=5, help="Number of results (default: 5)")
@click.option("--tag", "-t", default=None, help="Filter by tag")
@click.option("--context-only", is_flag=True,
              help="Output raw context block — pipe to clipboard or file")
def ask(query, top_k, tag, context_only):
    """Search the knowledge base.

    \b
    Examples:
      python3 cortex.py ask "design system button component"
      python3 cortex.py ask "MFE state pattern" --tag standards
      python3 cortex.py ask "auth flow" --context-only | pbcopy
      python3 cortex.py ask "form validation" --context-only > .context.md
    """
    from cortex.query import retrieve
    retrieve(query=query, top_k=top_k, tag=tag, context_only=context_only)


# ─── SYNC ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show chunk counts per file")
@click.option("--knowledge", "-k", is_flag=True, help="Sync knowledge/ files instead of specs")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output (used by post-merge hook)")
def sync(verbose, knowledge, quiet):
    """Sync changed specs (or knowledge/ files) back into the DB.

    \b
    Detects changes via file hash — safe to run repeatedly.
    Unchanged files are always skipped.

    \b
    Examples:
      python3 cortex.py sync                    # sync stale specs
      python3 cortex.py sync --knowledge        # sync stale knowledge/ files
      python3 cortex.py sync --knowledge --quiet
    """
    if knowledge:
        from cortex.spec import cmd_sync_knowledge
        cmd_sync_knowledge(verbose=verbose, quiet=quiet)
    else:
        from cortex.spec import cmd_sync
        cmd_sync(verbose=verbose)


# ─── WATCH ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--interval", default=1.0, help="Poll interval in seconds (default: 1.0)")
@click.option("--knowledge", "-k", is_flag=True, help="Also watch knowledge/ files")
def watch(interval, knowledge):
    """Auto-sync specs (and optionally knowledge/) on file save.

    \b
    Run in a dedicated terminal panel.

    \b
    Examples:
      python3 cortex.py watch                   # watch specs/ only
      python3 cortex.py watch --knowledge       # watch specs/ + knowledge/
    """
    from cortex.spec import cmd_watch
    cmd_watch(interval=interval, knowledge=knowledge)


# ─── LS ───────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--specs", is_flag=True, help="Show spec files and their DB sync status")
def ls(specs):
    """List indexed documents or spec files.

    \b
    Examples:
      python3 cortex.py ls              # all indexed documents
      python3 cortex.py ls --specs      # spec files with sync status
    """
    if specs:
        from cortex.spec import cmd_list
        cmd_list()
        return

    from cortex.db import get_client
    from rich.table import Table

    client = get_client()
    try:
        col = client.get_collection("cortex")
        results = col.get(include=["metadatas"])
        counts: dict = {}
        tags: dict = {}
        for m in results["metadatas"]:
            src = m.get("source", "unknown")
            counts[src] = counts.get(src, 0) + 1
            tags[src] = m.get("tag", "—")

        table = Table(title="[cyan]cortex knowledge base[/cyan]")
        table.add_column("Source", style="dim")
        table.add_column("Tag", style="yellow")
        table.add_column("Chunks", justify="right", style="green")

        for src in sorted(counts):
            table.add_row(src, tags[src], str(counts[src]))

        table.add_section()
        table.add_row("[bold]TOTAL[/bold]", "", f"[bold]{len(results['metadatas'])}[/bold]")
        console.print()
        console.print(table)
        console.print()
    except Exception:
        console.print("[red]No DB found. Run: python3 cortex.py add <path>[/red]")


# ─── STATS ────────────────────────────────────────────────────────────────────

@cli.command()
def stats():
    """Show knowledge base statistics.

    \b
    Example:
      python3 cortex.py stats
    """
    from cortex.db import get_client
    client = get_client()
    try:
        col = client.get_collection("cortex")
        results = col.get(include=["metadatas"])
        sources = set(m.get("source") for m in results["metadatas"])
        tags: dict = {}
        for m in results["metadatas"]:
            t = m.get("tag", "untagged")
            tags[t] = tags.get(t, 0) + 1

        console.print(f"\n[cyan]cortex stats[/cyan]")
        console.print(f"  [green]documents:[/green]  {len(sources)}")
        console.print(f"  [green]chunks:[/green]     {len(results['metadatas'])}")
        console.print(f"  [green]model:[/green]      all-MiniLM-L6-v2 (384d, local)")
        from cortex.db import _project_name
        console.print(f"  [green]storage:[/green]    ~/.cortex/{_project_name()}/chroma")
        console.print(f"  [green]by tag:[/green]")
        for t, n in sorted(tags.items()):
            console.print(f"    [dim]{t}:[/dim] {n} chunks")
        console.print()
    except Exception:
        console.print("[red]No DB found. Run: python3 cortex.py add <path>[/red]")


# ─── RM ───────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("source")
def rm(source):
    """Remove a source file's chunks from the DB.

    \b
    Example:
      python3 cortex.py rm specs/PROJ-1234-2025-01-15-old-spec.md
      python3 cortex.py rm knowledge/standards/deprecated.md
    """
    from cortex.db import get_client
    client = get_client()
    try:
        col = client.get_collection("cortex")
        existing = col.get(where={"source": source}, include=["metadatas"])
        if not existing["metadatas"]:
            console.print(f"[yellow]Not found:[/yellow] {source}")
            return
        col.delete(where={"source": source})
        console.print(f"[green]✓[/green] Removed: [yellow]{source}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


# ─── GENERATE ─────────────────────────────────────────────────────────────────

@cli.group()
def generate():
    """Regenerate a stable knowledge artifact from the DB.

    \b
    These are manually triggered — never auto-regenerated.
    Edit TOPICS config in cortex/generate.py to tune output.
    """
    pass


@generate.command(name="standards")
@click.option("--yes", "-y", is_flag=True, help="Skip overwrite confirmation")
def gen_standards(yes):
    """Regenerate knowledge/standards/STANDARDS.md

    \b
    Example:
      python3 cortex.py generate standards
    """
    from cortex.generate import cmd_standards
    cmd_standards(yes=yes)


@generate.command(name="vision")
@click.option("--yes", "-y", is_flag=True, help="Skip overwrite confirmation")
def gen_vision(yes):
    """Regenerate knowledge/vision/VISION.md

    \b
    Example:
      python3 cortex.py generate vision
    """
    from cortex.generate import cmd_vision
    cmd_vision(yes=yes)


@generate.command(name="adr")
@click.option("--yes", "-y", is_flag=True, help="Skip overwrite confirmation")
def gen_adr(yes):
    """Regenerate knowledge/adrs/ADR-INDEX.md

    \b
    Example:
      python3 cortex.py generate adr
    """
    from cortex.generate import cmd_adr
    cmd_adr(yes=yes)


@generate.command(name="all")
@click.option("--yes", "-y", is_flag=True, help="Skip all confirmations")
def gen_all(yes):
    """Regenerate all three artifacts.

    \b
    Example:
      python3 cortex.py generate all --yes
    """
    from cortex.generate import cmd_all
    cmd_all(yes=yes)


# ─── INIT ─────────────────────────────────────────────────────────────────────

@cli.command()
def init():
    """Create cortex folder structure in the current repo.

    \b
    Creates:
      knowledge/standards/        → coding standards
      knowledge/design-system/    → design system docs
      knowledge/adrs/             → architecture decisions
      knowledge/vision/           → product vision + personas
      knowledge/skills/           → team skills + processes
      knowledge/patterns/         → implementation patterns
      knowledge/team-conventions/ → team conventions
      specs/                      → feature specs
      .github/prompts/            → Copilot Chat prompt files

    \b
    Example:
      python3 cortex.py init
    """
    from pathlib import Path

    folders = [
        ("cortex/knowledge/standards",        "# Standards\n\nDocument your team's coding standards here.\n"),
        ("cortex/knowledge/design-system",    "# Design System\n\nDocument your design system components here.\n"),
        ("cortex/knowledge/adrs",             "# Architecture Decision Records\n\nDocument architectural decisions here.\n"),
        ("cortex/knowledge/vision",           "# Vision\n\nDocument product vision, personas, and capabilities here.\n"),
        ("cortex/knowledge/skills",           "# Skills\n\nDocument team skills and processes here.\n"),
        ("cortex/knowledge/patterns",         "# Patterns\n\nDocument implementation patterns here.\n"),
        ("cortex/knowledge/team-conventions", "# Team Conventions\n\nDocument team norms and conventions here.\n"),
        ("cortex/specs",                      None),
        (".github/prompts",                   None),
    ]

    console.print("\n[cyan]cortex init[/cyan]\n")
    any_created = False
    for folder, readme_content in folders:
        p = Path(folder)
        if p.exists():
            console.print(f"  [dim]exists [/dim] {folder}/")
            continue
        p.mkdir(parents=True, exist_ok=True)
        if readme_content:
            (p / "README.md").write_text(readme_content)
        console.print(f"  [green]created[/green] {folder}/")
        any_created = True

    console.print()
    if any_created:
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Add your knowledge files to cortex/knowledge/<subfolder>/")
        console.print("  2. python3 cortex.py add ./cortex/knowledge/standards --tag standards")
        console.print("     python3 cortex.py add ./cortex/knowledge/design-system --tag design-system")
        console.print("     (repeat for each subfolder)")
        console.print("  3. python3 cortex.py install-hook    ← git pre-commit + post-merge hooks")
        console.print("  4. python3 cortex.py audit           ← verify coverage")
        console.print()
        console.print("[dim]Optional — link other repos to query their DBs alongside this one:[/dim]")
        console.print("[dim]  python3 cortex.py repos add <repo-name>   (run manually, then commit .cortex-repos.json)[/dim]\n")
    else:
        console.print("[green]✓ All folders already exist.[/green]\n")


# ─── BOOTSTRAP ────────────────────────────────────────────────────────────────

@cli.command()
def bootstrap():
    """Get fully operational after cloning an existing cortex repo.

    \b
    Distinct from `init` (which creates folders for a brand-new repo).
    bootstrap is for developers who just cloned a repo that already uses cortex.

    \b
    Steps:
      1. Ingest current repo's knowledge/ subfolders
      2. Sync knowledge in linked repos with known local paths
      3. Install git pre-commit + post-merge hooks

    \b
    Safe to re-run — unchanged files are always skipped.

    \b
    Example:
      python3 cortex.py bootstrap
    """
    import subprocess
    from pathlib import Path
    from cortex.spec import KNOWLEDGE_TAG_MAP
    from cortex.ingest import ingest_paths
    from cortex.config import load_linked, load_local_paths
    from cortex.hook import cmd_install

    python = str(Path("cortex/.venv/bin/python")) if Path("cortex/.venv/bin/python").exists() else "python3"

    console.print("\n[cyan]cortex bootstrap[/cyan]\n")

    # Step 1 — ingest current repo knowledge
    console.print("[bold]Step 1[/bold]  Ingesting current repo knowledge...\n")
    any_knowledge = False
    for folder, tag in KNOWLEDGE_TAG_MAP.items():
        path = Path("cortex/knowledge") / folder
        if path.exists():
            ingest_paths([str(path)], tag=tag, force=False)
            any_knowledge = True
        else:
            console.print(f"  [dim]skip[/dim]  cortex/knowledge/{folder}/ [dim](not found)[/dim]")
    if not any_knowledge:
        console.print("  [yellow]No cortex/knowledge/ subfolders found. Run `python3 cortex.py init` first.[/yellow]")

    # Step 2 — sync linked repos
    console.print("\n[bold]Step 2[/bold]  Syncing linked repos...\n")
    linked = load_linked()
    local_paths = load_local_paths()
    skipped_repos = []
    if not linked:
        console.print("  [dim]No linked repos configured.[/dim]")
    for entry in linked:
        name = entry["name"]
        path = local_paths.get(name)
        if not path or not Path(path).exists():
            skipped_repos.append(name)
            continue
        console.print(f"  [cyan]→[/cyan] {name}  [dim]({path})[/dim]")
        subprocess.run([python, "cortex.py", "sync", "--knowledge"], cwd=path)

    # Step 3 — install hooks
    console.print("\n[bold]Step 3[/bold]  Installing git hooks...\n")
    cmd_install()

    # Summary
    console.print("\n[green]✓ Bootstrap complete.[/green]")
    if skipped_repos:
        console.print(f"\n[yellow]Linked repos with no local path registered:[/yellow] {', '.join(skipped_repos)}")
        console.print("[dim]  Register paths: python3 cortex.py repos add <local/path/to/repo>[/dim]")
        console.print("[dim]  Then sync:      python3 cortex.py repos sync[/dim]")
    console.print()


# ─── AUDIT ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--threshold", default=5, help="Chunks below this count = sparse (default: 5)")
def audit(threshold):
    """Show knowledge tag coverage — flag empty or sparse tags.

    \b
    Example:
      python3 cortex.py audit
      python3 cortex.py audit --threshold 10
    """
    from rich.table import Table

    EXPECTED_TAGS = [
        "standards", "design-system", "adr", "vision",
        "skills", "patterns", "team-conventions", "spec",
    ]

    from cortex.db import get_client
    client = get_client()
    try:
        col = client.get_collection("cortex")
        results = col.get(include=["metadatas"])
    except Exception:
        console.print("[red]No DB found. Run: python3 cortex.py add <path>[/red]")
        return

    tag_counts: dict = {}
    for m in results["metadatas"]:
        t = m.get("tag", "untagged")
        tag_counts[t] = tag_counts.get(t, 0) + 1

    table = Table(title="[cyan]cortex audit — knowledge coverage[/cyan]")
    table.add_column("Tag", style="yellow")
    table.add_column("Chunks", justify="right")
    table.add_column("Status", justify="center")

    issues = []
    for tag in EXPECTED_TAGS:
        count = tag_counts.get(tag, 0)
        if count == 0:
            status = "[red]EMPTY[/red]"
            issues.append((tag, f"not ingested — run: python3 cortex.py add ./cortex/knowledge/<folder> --tag {tag}"))
        elif count < threshold:
            status = "[yellow]SPARSE[/yellow]"
            issues.append((tag, f"only {count} chunk(s) — consider adding more content"))
        else:
            status = "[green]✓[/green]"
        table.add_row(tag, str(count), status)

    for tag in sorted(tag_counts):
        if tag not in EXPECTED_TAGS:
            table.add_row(f"[dim]{tag}[/dim]", str(tag_counts[tag]), "[dim]extra[/dim]")

    console.print()
    console.print(table)
    console.print()

    if issues:
        console.print("[bold]Gaps to address:[/bold]")
        for tag, msg in issues:
            console.print(f"  [yellow]→[/yellow] [yellow]{tag}[/yellow]: {msg}")
        console.print()
    else:
        console.print(f"[green]✓ All expected tags have ≥ {threshold} chunks.[/green]\n")


# ─── REPOS ────────────────────────────────────────────────────────────────────

@cli.group()
def repos():
    """Manage cross-repo DB links for this project.

    \b
    Links are stored in .cortex-repos.json (committed in the repo root).
    Linked repos are queried by name — cortex resolves ~/.cortex/{name}/chroma
    at query time, so the config works on any machine without path changes.
    """
    pass


@repos.command(name="add")
@click.argument("name_or_path")
@click.option("--tags", "-t", default=None,
              help="Comma-separated tags to pull from this repo (default: all). "
                   "Example: --tags standards,adr")
def repos_add(name_or_path, tags):
    """Link another repo's DB to this project's queries.

    \b
    Pass the repo name (git root folder name) or a local path to the repo.
    If a path is given, the name is derived from the git root automatically.

    \b
    Examples:
      python3 cortex.py repos add design-system
      python3 cortex.py repos add ../design-system
      python3 cortex.py repos add shared-platform --tags standards,adr
    """
    from cortex.config import add_linked
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    entry = add_linked(name_or_path, tags=tag_list)
    if entry is None:
        console.print(f"[yellow]Already linked:[/yellow] {name_or_path}")
        return
    tags_label = f"  tags: {', '.join(entry['tags'])}" if entry.get("tags") else "  tags: all"
    console.print(f"\n[green]✓ Linked:[/green] [cyan]{entry['name']}[/cyan]")
    console.print(f"  {tags_label}")
    console.print(f"  DB: ~/.cortex/{entry['name']}/chroma")
    console.print(f"\n  Saved to: .cortex-repos.json\n")


@repos.command(name="rm")
@click.argument("name")
def repos_rm(name):
    """Remove a linked repo from this project's queries.

    \b
    Example:
      python3 cortex.py repos rm design-system
    """
    from cortex.config import remove_linked
    if remove_linked(name):
        console.print(f"\n[green]✓ Unlinked:[/green] [cyan]{name}[/cyan]\n")
    else:
        console.print(f"\n[yellow]Not found:[/yellow] {name} — run 'cortex repos ls' to see current links\n")


@repos.command(name="ls")
def repos_ls():
    """List linked repos and whether their DB exists locally.

    \b
    Example:
      python3 cortex.py repos ls
    """
    from pathlib import Path
    from rich.table import Table
    from cortex.config import load_linked
    from cortex.db import _project_name

    linked = load_linked()
    current = _project_name()

    console.print(f"\n[cyan]cortex repos[/cyan] · [dim]current project: {current}[/dim]\n")

    if not linked:
        console.print("[dim]No linked repos. Add one: python3 cortex.py repos add <name>[/dim]\n")
        return

    table = Table()
    table.add_column("Repo", style="cyan")
    table.add_column("Tags filter", style="dim")
    table.add_column("DB available", justify="center")
    table.add_column("Chunks", justify="right")

    for entry in linked:
        name = entry["name"]
        tag_filter = ", ".join(entry["tags"]) if entry.get("tags") else "[dim]all[/dim]"
        db_path = Path.home() / ".cortex" / name / "chroma"
        if db_path.exists():
            try:
                import chromadb
                client = chromadb.PersistentClient(path=str(db_path))
                col = client.get_collection("cortex")
                chunks = str(col.count())
                available = "[green]✓[/green]"
            except Exception:
                chunks = "?"
                available = "[yellow]error[/yellow]"
        else:
            available = "[red]not ingested[/red]"
            chunks = "—"
        table.add_row(name, tag_filter, available, chunks)

    console.print(table)
    console.print()
    console.print(f"[dim]Config: .cortex-repos.json (committed)[/dim]")
    console.print(f"[dim]DBs resolve to: ~/.cortex/{{name}}/chroma[/dim]\n")


@repos.command(name="sync")
def repos_sync():
    """Re-ingest knowledge from all linked repos with known local paths.

    \b
    Local paths are recorded automatically when you run `repos add <path>`.
    Repos added by name only (no path) are skipped with a hint.

    \b
    Example:
      python3 cortex.py repos sync
    """
    import subprocess
    from pathlib import Path
    from cortex.config import load_linked, load_local_paths

    linked = load_linked()
    if not linked:
        console.print("[dim]No linked repos. Add one: python3 cortex.py repos add <path>[/dim]")
        return

    local_paths = load_local_paths()
    python = str(Path("cortex/.venv/bin/python")) if Path("cortex/.venv/bin/python").exists() else "python3"

    synced = []
    skipped = []
    console.print()
    for entry in linked:
        name = entry["name"]
        path = local_paths.get(name)
        if not path or not Path(path).exists():
            skipped.append(name)
            continue
        console.print(f"[cyan]→[/cyan] Syncing [bold]{name}[/bold]  [dim]({path})[/dim]")
        subprocess.run([python, "cortex.py", "sync", "--knowledge"], cwd=path)
        synced.append(name)

    console.print()
    if synced:
        console.print(f"[green]✓[/green] Synced: {', '.join(synced)}")
    if skipped:
        console.print(f"[yellow]⚠ Skipped (no local path):[/yellow] {', '.join(skipped)}")
        console.print(f"[dim]  Register paths by running: python3 cortex.py repos add <local/path/to/repo>[/dim]")
    console.print()


# ─── HOOK ─────────────────────────────────────────────────────────────────────

@cli.command(name="install-hook")
def install_hook():
    """Install git pre-commit and post-merge hooks.

    \b
    pre-commit  prompts to sync stale specs + knowledge before commit
    post-merge  auto-ingests knowledge/ changes after git pull / merge

    \b
    Example:
      python3 cortex.py install-hook
    """
    from cortex.hook import cmd_install
    cmd_install()


@cli.command(name="uninstall-hook")
def uninstall_hook():
    """Remove cortex git hooks (pre-commit and post-merge).

    \b
    Example:
      python3 cortex.py uninstall-hook
    """
    from cortex.hook import cmd_uninstall
    cmd_uninstall()


@cli.command(name="hook-run", hidden=True)
def hook_run():
    """Internal: called by the pre-commit hook script."""
    from cortex.hook import cmd_run
    sys.exit(cmd_run())


# ─── RESET ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def reset(yes):
    """Delete the local ChromaDB — all ingested chunks are removed.

    \b
    The DB is recreated automatically next time you run `add` or `bootstrap`.

    \b
    Example:
      python3 cortex.py reset
      python3 cortex.py reset --yes
    """
    import shutil
    from cortex.db import _cortex_dir, _project_name

    path = _cortex_dir()
    if not path.exists():
        console.print("[yellow]No DB found — nothing to reset.[/yellow]")
        return

    console.print(f"\n[red]This will delete:[/red] {path}")
    if not yes and not click.confirm("Reset the cortex DB?", default=False):
        console.print("[dim]Aborted.[/dim]\n")
        return

    shutil.rmtree(path)
    console.print(f"[green]✓ DB reset.[/green] Run [cyan]python3 cortex.py bootstrap[/cyan] to re-ingest.\n")


# ─── ENTRYPOINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
