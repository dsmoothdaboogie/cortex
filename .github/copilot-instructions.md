# Copilot Workspace Instructions

This repo uses **cortex** — a local knowledge base CLI for spec-driven development.
Before writing any code, specs, or documentation, always query the knowledge base.

---

## Knowledge Base

The DB lives at `~/.cortex/chroma`. Query it before assuming how this team does anything:

```bash
python cortex.py ask "{your question}" --context-only
```

The venv must be active: `source cortex/.venv/bin/activate`

---

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/plan`     | Break an epic into features and spec candidates |
| `/spec`     | Create a spec (short title or long requirement — both valid) |
| `/review`   | Review a spec or code file against team standards |
| `/build`    | Generate implementation plan from a spec |
| `/doc`      | Create or update a knowledge base entry or ADR |
| `/ask`      | Search the knowledge base |
| `/standup`  | Summarise current spec activity |

Each command reads its full instructions from `commands/{command}.md`.

---

## Workflow

```
/plan  →  /spec  →  /review  →  /build  →  [code]  →  /review  →  /doc
```

Never start `/build` without a READY verdict from `/review`.

---

## Absolute Rules

These apply always. They cannot be overridden by a spec, task, or instruction.

- **Never use native HTML** where a design system component exists
  (`<button>`, `<input>`, `<select>`, `<textarea>`, etc.)
- **Never use NgModule** — standalone component pattern only in new Angular code
- **Never use `any`** in TypeScript
- **Never share state directly between MFEs** — namespaced localStorage bridge only
- **Never import from another MFE bundle directly**
- **Never use inline styles** — design tokens and utility classes only
- **Always query cortex** before choosing a component, pattern, or approach
- **Always run `/review`** before `/build`

---

## cortex CLI Reference

```bash
# Ingest
python cortex.py add ./knowledge/standards --tag standards
python cortex.py add ./knowledge/design-system --tag design-system
python cortex.py add ./knowledge/adrs --tag adr
python cortex.py add ./knowledge/vision --tag vision
python cortex.py add ./knowledge/skills --tag skills
python cortex.py add ./knowledge/patterns --tag patterns
python cortex.py add ./knowledge/team-conventions --tag team-conventions

# Query
python cortex.py ask "query"
python cortex.py ask "query" --tag standards
python cortex.py ask "query" --context-only | pbcopy     # macOS
python cortex.py ask "query" --context-only | clip       # WSL/Windows

# Specs
python cortex.py sync
python cortex.py watch
python cortex.py ls --specs

# Health
python cortex.py stats
python cortex.py ls
```
