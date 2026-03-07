"""
hook.py — Pre-commit and post-merge hook installers
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

# Shared with spec.py — import to avoid duplication
from cortex.spec import KNOWLEDGE_TAG_MAP


def _staged_knowledge_folders() -> list[str]:
    """Return sorted list of knowledge subfolders that have staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True,
        )
        changed = result.stdout.strip().splitlines()
    except Exception:
        return []

    folders: set[str] = set()
    for f in changed:
        parts = Path(f).parts
        if len(parts) >= 2 and parts[0] == "knowledge":
            subfolder = parts[1]
            if subfolder in KNOWLEDGE_TAG_MAP:
                folders.add(subfolder)
    return sorted(folders)

HOOK_SCRIPT = """\
#!/bin/sh
# cortex pre-commit hook
VENV_PYTHON="cortex/.venv/bin/python"
PYTHON=$( [ -f "$VENV_PYTHON" ] && echo "$VENV_PYTHON" || echo "python3" )
$PYTHON cortex.py hook-run
exit $?
"""

POST_MERGE_SCRIPT = """\
#!/bin/sh
# cortex post-merge hook — re-ingests knowledge/ changes pulled from teammates
VENV_PYTHON="cortex/.venv/bin/python"
PYTHON=$( [ -f "$VENV_PYTHON" ] && echo "$VENV_PYTHON" || echo "python3" )
$PYTHON cortex.py sync --knowledge --quiet
exit 0
"""

HOOK_PATH = Path(".git/hooks/pre-commit")
POST_MERGE_PATH = Path(".git/hooks/post-merge")


def _install_hook(path: Path, script: str, label: str):
    if path.exists():
        backup = path.with_suffix(".backup")
        path.rename(backup)
        console.print(f"[yellow]Existing {label} hook backed up → {backup}[/yellow]")
    path.parent.mkdir(exist_ok=True)
    path.write_text(script)
    path.chmod(0o755)
    console.print(f"[green]✓ {label} hook installed:[/green] {path}")


def cmd_install():
    if not Path(".git").exists():
        console.print("[red]Not a git repository.[/red]")
        return
    console.print()
    _install_hook(HOOK_PATH, HOOK_SCRIPT, "pre-commit")
    _install_hook(POST_MERGE_PATH, POST_MERGE_SCRIPT, "post-merge")
    console.print()
    console.print("[dim]pre-commit:[/dim]  prompts to sync stale specs and knowledge changes before commit")
    console.print("[dim]post-merge:[/dim]  auto-ingests knowledge/ changes after git pull / merge\n")


def cmd_uninstall():
    console.print()
    for path, label in [(HOOK_PATH, "pre-commit"), (POST_MERGE_PATH, "post-merge")]:
        if not path.exists():
            console.print(f"[yellow]No {label} hook found.[/yellow]")
            continue
        if "cortex" not in path.read_text():
            console.print(f"[yellow]{label} hook not installed by cortex — leaving it.[/yellow]")
            continue
        path.unlink()
        backup = path.with_suffix(".backup")
        if backup.exists():
            backup.rename(path)
        console.print(f"[green]✓ {label} hook removed.[/green]")
    console.print()


def cmd_run() -> int:
    from cortex.spec import cmd_sync_check, cmd_sync

    # --- stale spec check ---
    stale = cmd_sync_check()
    if stale:
        sys.stderr.write("\n\033[33mcortex:\033[0m Stale specs detected:\n")
        for s in stale:
            sys.stderr.write(f"  → {s}\n")
        sys.stderr.write("\n")

        try:
            sys.stderr.write("\033[36mSync specs to DB before commit?\033[0m [y/N]: ")
            sys.stderr.flush()
            answer = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            return 0

        if answer == "y":
            synced = cmd_sync(verbose=False)
            if synced > 0:
                for s in stale:
                    subprocess.run(["git", "add", str(s)], capture_output=True)
                sys.stderr.write(f"\n\033[32m✓\033[0m {synced} spec(s) synced and staged.\n\n")

    # --- staged knowledge check ---
    folders = _staged_knowledge_folders()
    if folders:
        sys.stderr.write("\n\033[33mcortex:\033[0m Knowledge files staged — DB may be out of date:\n")
        for folder in folders:
            sys.stderr.write(f"  → knowledge/{folder}/\n")
        sys.stderr.write("\n")

        try:
            sys.stderr.write("\033[36mRe-ingest knowledge to keep DB in sync?\033[0m [y/N]: ")
            sys.stderr.flush()
            answer = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            return 0

        if answer == "y":
            python = "cortex/.venv/bin/python" if Path("cortex/.venv/bin/python").exists() else "python3"
            for folder in folders:
                tag = KNOWLEDGE_TAG_MAP[folder]
                path = f"knowledge/{folder}"
                subprocess.run([python, "cortex.py", "add", path, "--tag", tag, "--force"])
                subprocess.run(["git", "add", path], capture_output=True)
            sys.stderr.write(f"\n\033[32m✓\033[0m Knowledge re-ingested and staged.\n\n")

    return 0
