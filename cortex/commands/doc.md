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

1. Pull existing context to avoid duplication:
   ```
   python cortex.py ask "{topic}" --context-only
   ```
2. Check if a similar entry exists. If it does, suggest `--update` instead.
3. Write the entry using the wiki template below.
4. Save to the appropriate `cortex/knowledge/` subfolder.
5. Ingest: `python cortex.py add {path} --tag {tag} --force`

### ADR (--adr flag)

1. Pull related decisions:
   ```
   python cortex.py ask "{decision topic}" --tag adr --context-only
   ```
2. Check for existing ADRs that this supersedes or relates to.
3. Write the ADR using the ADR template below.
4. Save to: `cortex/knowledge/adrs/adr-{NNN}-{slug}.md`
5. Ingest: `python cortex.py add cortex/knowledge/adrs/{filename}.md --tag adr`

### Update existing (--update <file>)

1. Read the existing file
2. Pull current context: `python cortex.py ask "{topic}" --context-only`
3. Merge new information — preserve existing content, add new sections
4. Re-ingest: `python cortex.py add {file} --force`

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
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), fall back to reading `cortex/knowledge/` files directly to check for duplicates before writing. Skip the ingest steps — note that the DB is unavailable and the file should be ingested manually once the environment is active
- ADR numbers must be sequential — check `cortex/knowledge/adrs/` before numbering
- Never duplicate existing content — update instead
