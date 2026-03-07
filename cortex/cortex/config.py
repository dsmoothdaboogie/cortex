"""
config.py — Per-repo cross-repo link configuration

Stored at .cortex-repos.json in the repo root (committed).
References linked repos by name (git root folder name), not path,
so the config works on any machine without modification.

At query time, cortex resolves ~/.cortex/{name}/chroma for each linked repo.

Local path registry (.cortex-repos-local.json) is machine-specific and gitignored.
It records the local filesystem path for each linked repo, used by `repos sync`.
Written automatically when you run `repos add <path>`.
"""

import json
from pathlib import Path


CONFIG_FILE = Path(".cortex-repos.json")
LOCAL_CONFIG_FILE = Path(".cortex-repos-local.json")


def load_linked() -> list[dict]:
    """Return list of {"name": str, "tags": list[str] | None}"""
    if not CONFIG_FILE.exists():
        return []
    try:
        return json.loads(CONFIG_FILE.read_text()).get("linked", [])
    except Exception:
        return []


def save_linked(linked: list[dict]):
    CONFIG_FILE.write_text(json.dumps({"linked": linked}, indent=2) + "\n")


def load_local_paths() -> dict[str, str]:
    """Return machine-local {name: absolute_path} mapping (from .cortex-repos-local.json)."""
    if not LOCAL_CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(LOCAL_CONFIG_FILE.read_text()).get("paths", {})
    except Exception:
        return {}


def save_local_path(name: str, path: str):
    """Record the local filesystem path for a linked repo (machine-local, gitignored)."""
    data = load_local_paths()
    data[name] = path
    LOCAL_CONFIG_FILE.write_text(json.dumps({"paths": data}, indent=2) + "\n")


def add_linked(name_or_path: str, tags: list[str] | None = None) -> dict | None:
    """Add a repo by name or local path. Returns new entry or None if already linked."""
    # If it looks like a path, derive the name from the git root or folder name
    p = Path(name_or_path)
    resolved_path: str | None = None
    if p.exists() and p.is_dir():
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(p)
        )
        if result.returncode == 0:
            git_root = Path(result.stdout.strip())
            name = git_root.name
            resolved_path = str(git_root.resolve())
        else:
            name = p.name
            resolved_path = str(p.resolve())
    else:
        name = name_or_path  # treat as a bare name

    linked = load_linked()
    if any(e["name"] == name for e in linked):
        return None  # already linked

    entry: dict = {"name": name}
    if tags:
        entry["tags"] = tags
    linked.append(entry)
    save_linked(linked)

    # Store the local path in machine-local config (used by `repos sync`)
    if resolved_path:
        save_local_path(name, resolved_path)

    return entry


def remove_linked(name: str) -> bool:
    """Remove by name. Returns True if something was removed."""
    linked = load_linked()
    before = len(linked)
    linked = [e for e in linked if e["name"] != name]
    if len(linked) == before:
        return False
    save_linked(linked)
    return True
