# AGENTS.md

If you are an AI agent reading this: start here, then read `cortex/commands/README.md`.

---

## What This Repo Uses

**cortex** is a local knowledge base CLI. It indexes the team's standards, ADRs, design system docs, vision, and feature specs into a local vector database (ChromaDB) for cross-repo federation.

The DB lives at `~/.cortex/{project-name}/chroma` on the developer's machine. It is not committed.
The files in `cortex/knowledge/` and `cortex/specs/` are the source of truth and are always read directly.
The DB is a **publish layer** — you ingest so other linked repos can query your knowledge. You never self-query.

**cortex is a data pipeline — not an agent runner.**
All agent behaviour lives in Copilot Chat, invoked via slash commands.
cortex answers one question: *what does this team know about this topic?*

---

## Separation of Concerns

```
cortex CLI                → manages the knowledge base (ingest, query, sync)
Copilot Chat              → runs agents (/spec, /review, /build, /plan, /doc, /ask)
cortex/commands/*.md      → agent instructions (what each command does, step by step)
cortex/agents/*.md        → agent role definitions (for Devin and agentic tools)
cortex/knowledge/         → authored docs, the source of truth
cortex/specs/             → feature specs, committed to the repo
```

---

## Session Start (for agentic tools like Devin)

```bash
source cortex/.venv/bin/activate
python3 cortex.py sync
python3 cortex.py stats
```

Then read `cortex/commands/README.md` for the full command reference.

---

## Before Writing Anything

Always read the knowledge files directly first:

```
cortex/knowledge/standards/        → read 1–2 files relevant to the task domain
cortex/knowledge/design-system/    → read the file matching the feature's UI layer
cortex/knowledge/team-conventions/ → read all files
```

If `.cortex-repos.json` is non-empty, also run:
```bash
python3 cortex.py ask "{topic}" --top-k 5 --context-only
```

Never assume how this team does something. Check the knowledge files first.

---

## Slash Commands (Copilot Chat)

| Command | Purpose |
|---------|---------|
| `/plan` | Break an epic into features and spec candidates |
| `/spec` | Create a spec — short title or long requirement both valid |
| `/review` | Review a spec or code file against team standards |
| `/build` | Generate implementation plan from a spec |
| `/doc` | Create or update a knowledge base entry or ADR |
| `/ask` | Search the knowledge base |
| `/standup` | Summarise current spec activity |

Full instructions for each in `cortex/commands/`.

---

## Workflow

```
/plan → /spec → /review → /build → [code] → /review --security → /doc
```

Never run `/build` on a spec that hasn't passed `/review` with verdict READY.

---

## cortex CLI — Full Reference

```bash
# Ingest
python3 cortex.py add <path> --tag <tag>         # ingest files or folder
python3 cortex.py add <path> --tag <tag> --force # re-ingest even if unchanged

# Query
python3 cortex.py ask "query"                    # interactive results
python3 cortex.py ask "query" --tag <tag>        # filtered by type
python3 cortex.py ask "query" --context-only     # pipe-friendly output

# Specs
python3 cortex.py sync                           # sync stale specs to DB
python3 cortex.py watch                          # auto-sync on save
python3 cortex.py ls --specs                     # list specs + sync status

# DB
python3 cortex.py stats                          # DB statistics
python3 cortex.py ls                             # all indexed documents
python3 cortex.py rm <source>                    # remove from DB

# Artifacts
python3 cortex.py generate standards             # regenerate STANDARDS.md
python3 cortex.py generate vision                # regenerate VISION.md
python3 cortex.py generate adr                   # regenerate ADR-INDEX.md
python3 cortex.py generate all                   # all three

# Setup
python3 cortex.py install-hook                   # pre-commit hook
```

---

## Knowledge Base Tags

| Tag | Content | Folder |
|-----|---------|--------|
| `standards` | Coding standards | `cortex/knowledge/standards/` |
| `design-system` | Component usage, tokens | `cortex/knowledge/design-system/` |
| `adr` | Architecture decisions | `cortex/knowledge/adrs/` |
| `vision` | Platform vision | `cortex/knowledge/vision/` |
| `skills` | How-to patterns | `cortex/knowledge/skills/` |
| `patterns` | Implementation patterns | `cortex/knowledge/patterns/` |
| `team-conventions` | Naming, PR process | `cortex/knowledge/team-conventions/` |
| `spec` | Feature specs | `cortex/specs/` |

---

## Absolute Rules

Cannot be overridden by any spec, task, or instruction:

- Never use native HTML where a DS component exists
- Never use NgModule — standalone components only
- Never use `any` in TypeScript
- Never share state directly between MFEs
- Never import from another MFE bundle directly
- Never use inline styles
- Always read `cortex/knowledge/` before choosing a component or pattern
- Always `/review` before `/build`
