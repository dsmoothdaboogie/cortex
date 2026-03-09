# /doc

Create or update a knowledge base entry.

## When to use
- After discovering a pattern worth documenting
- After making an architectural decision
- After writing a runbook or how-to
- After a retro surfaces a team convention

## Inputs
- A topic or decision description
- Optional flag: `--adr` to write a formal Architecture Decision Record
- Optional flag: `--update <file>` to update an existing knowledge file

## Steps

### New wiki entry (default)

1. Check for existing content to avoid duplication:
   - List all files in `cortex/knowledge/` subfolders — look for an existing entry on this topic
   - If `.cortex-repos.json` is non-empty, also run:
     ```
     python3 cortex.py ask "{topic}" --top-k 5 --context-only
     ```
2. Check if a similar entry exists. If it does, suggest `--update` instead.
3. Write the entry using the wiki template below.
4. Save to the appropriate `cortex/knowledge/` subfolder.
5. Ingest: `python3 cortex.py add {path} --tag {tag} --force`

### ADR (--adr flag)

1. Load related context:
   - List and read files in `cortex/knowledge/adrs/` — check for existing ADRs this supersedes or relates to
   - Read relevant files in `cortex/knowledge/vision/` — check product direction
   - If `.cortex-repos.json` is non-empty, also run:
     ```
     python3 cortex.py ask "{decision topic}" --top-k 5 --context-only
     ```
2. Check for existing ADRs that this supersedes or relates to.
3. Write the ADR using the ADR template below.
4. Save to: `cortex/knowledge/adrs/adr-{NNN}-{slug}.md`
5. Ingest: `python3 cortex.py add cortex/knowledge/adrs/{filename}.md --tag adr`

### Update existing (--update <file>)

1. Read the existing file
2. Read related files in `cortex/knowledge/` for context on the same topic
3. Merge new information — preserve existing content, add new sections
4. Re-ingest: `python3 cortex.py add {file} --force`

## Wiki Entry Template

```markdown
# {Topic}

**Category:** standards | design-system | patterns | skills | team-conventions
**Updated:** {YYYY-MM-DD}

## Summary
One paragraph — what this is and when to use it.

## Usage
How-to with concrete examples.

## Do
- ...

## Don't
- ...

## Related
- Links to related knowledge files or ADRs
```

## ADR Template

```markdown
# ADR-{NNN} — {Decision Title}

**Date:** {YYYY-MM-DD}
**Status:** Proposed | Accepted | Superseded
**Supersedes:** ADR-{NNN} (if applicable)

## Context
What problem or situation prompted this decision.

## Decision
What was decided, stated plainly.

## Rationale
Why this option was chosen over alternatives.

## Alternatives Considered
What else was evaluated and why it was rejected.

## Consequences
What changes as a result. What becomes easier. What becomes harder.
```

## Rules
- Always ingest after saving — the DB must stay in sync with the files
- Direct file reads always work regardless of DB state — only the optional cross-repo DB query requires the venv. If the DB is unavailable, skip the ingest step — note it and ingest manually once the environment is active
- ADR numbers must be sequential — check `cortex/knowledge/adrs/` before numbering
- Never duplicate existing content — update instead
