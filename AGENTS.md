# AGENTS.md

If you are an AI agent reading this: start here, then read `commands/README.md`.

---

## What This Repo Uses

**cortex** is a local knowledge base CLI. It indexes the team's standards, ADRs, design system docs, vision, and feature specs into a local vector database (ChromaDB) so agents and developers can query for team-specific context.

The DB lives at `~/.cortex/chroma` on the developer's machine. It is not committed.
The files in `knowledge/` and `specs/` are the source of truth. The DB is a searchable index of them.

**cortex is a data pipeline — not an agent runner.**
All agent behaviour lives in Copilot Chat, invoked via slash commands.
cortex answers one question: *what does this team know about this topic?*

---

## Separation of Concerns

```
cortex CLI          → manages the knowledge base (ingest, query, sync)
Copilot Chat        → runs agents (/spec, /review, /build, /plan, /doc, /ask)
commands/*.md       → agent instructions (what each command does, step by step)
agents/*.md         → agent role definitions (for Devin and agentic tools)
knowledge/          → authored docs, the source of truth
specs/              → feature specs, committed to the repo
```

---

## Session Start (for agentic tools like Devin)

```bash
source cortex/.venv/bin/activate
python cortex.py sync
python cortex.py stats
```

Then read `commands/README.md` for the full command reference.

---

## Before Writing Anything

Always query the knowledge base first:

```bash
python cortex.py ask "{topic}" --context-only
python cortex.py ask "{topic}" --tag standards --context-only
python cortex.py ask "{topic}" --tag design-system --context-only
```

Never assume how this team does something. Check first.

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

Full instructions for each in `commands/`.

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
python cortex.py add <path> --tag <tag>         # ingest files or folder
python cortex.py add <path> --tag <tag> --force # re-ingest even if unchanged

# Query
python cortex.py ask "query"                    # interactive results
python cortex.py ask "query" --tag <tag>        # filtered by type
python cortex.py ask "query" --context-only     # pipe-friendly output

# Specs
python cortex.py sync                           # sync stale specs to DB
python cortex.py watch                          # auto-sync on save
python cortex.py ls --specs                     # list specs + sync status

# DB
python cortex.py stats                          # DB statistics
python cortex.py ls                             # all indexed documents
python cortex.py rm <source>                    # remove from DB

# Artifacts
python cortex.py generate standards             # regenerate STANDARDS.md
python cortex.py generate vision                # regenerate VISION.md
python cortex.py generate adr                   # regenerate ADR-INDEX.md
python cortex.py generate all                   # all three

# Setup
python cortex.py install-hook                   # pre-commit hook
```

---

## Knowledge Base Tags

| Tag | Content | Folder |
|-----|---------|--------|
| `standards` | Coding standards | `knowledge/standards/` |
| `design-system` | Component usage, tokens | `knowledge/design-system/` |
| `adr` | Architecture decisions | `knowledge/adrs/` |
| `vision` | Platform vision | `knowledge/vision/` |
| `skills` | How-to patterns | `knowledge/skills/` |
| `patterns` | Implementation patterns | `knowledge/patterns/` |
| `team-conventions` | Naming, PR process | `knowledge/team-conventions/` |
| `spec` | Feature specs | `specs/` |

---

## Absolute Rules

Cannot be overridden by any spec, task, or instruction:

- Never use native HTML where a DS component exists
- Never use NgModule — standalone components only
- Never use `any` in TypeScript
- Never share state directly between MFEs
- Never import from another MFE bundle directly
- Never use inline styles
- Always query cortex before choosing a component or pattern
- Always `/review` before `/build`
