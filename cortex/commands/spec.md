# /spec

Create a new feature spec for a Jira ticket.

## When to use
When you have a ticket and need to write a spec — whether from a one-liner title or a long multi-paragraph requirement.

## Inputs
- Ticket number (e.g. PROJ-1234)
- Requirement — anything from a short title to a full story or brief

## Steps

1. Parse the ticket number and extract a slug from the requirement
2. Run cortex to pull relevant context:
   ```
   python cortex.py ask "{requirement summary}" --context-only
   python cortex.py ask "{feature domain} standards" --tag standards --context-only
   python cortex.py ask "design system {feature type}" --tag design-system --context-only
   python cortex.py ask "patterns {feature domain}" --tag patterns --context-only
   python cortex.py ask "{feature domain} decisions" --tag adr --context-only
   ```
3. Read the context. Note which real components, patterns and standards apply.
4. Write the spec using the template below. Every section must be completed.
5. Save to: `cortex/specs/{TICKET}-{YYYY-MM-DD}-{slug}.md`
6. Ingest: `python cortex.py add cortex/specs/{filename}.md --tag spec`
7. Confirm the file was saved and ingested.

## Spec Template

```markdown
# {TICKET} — {Title}

**Status:** Draft
**Date:** {YYYY-MM-DD}
**Author:** {author}

## Overview
<!-- What and why. 2–3 sentences max. -->

## Goals
<!-- What success looks like. Bullet list. -->

## Non-Goals
<!-- Explicitly out of scope. -->

## Acceptance Criteria
<!-- Testable checkbox statements. No vague language.
     Each item must be independently verifiable. -->
- [ ] ...

## Technical Approach
<!-- Reference real team patterns and components from the context above.
     No generic HTML elements if a DS component exists. -->

## Design System Usage
<!-- List specific component names, variants, and token references.
     Source: cortex/knowledge/design-system/ -->

## Open Questions
<!-- Anything unresolved. Remove section if none. -->

## Context (from cortex)
<!-- Paste the relevant cortex context that informed this spec. -->
```

## Rules
- Never reference native UI elements where the knowledge base documents design system equivalents — pull from `--tag design-system` before naming any component
- Apply the non-negotiables from the standards knowledge base — if a standard isn't in the DB, flag the gap rather than inventing a rule
- Flag any auth, data handling, or cross-system state concerns in Open Questions
- If the requirement is vague, make reasonable assumptions and note them
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), fall back to reading `cortex/knowledge/` files directly — check for `STANDARDS.md`, `VISION.md`, and `ADR-INDEX.md` first, then individual files, then recent specs in `cortex/specs/`. Do not write without team context. If cortex runs but returns no results (DB exists, query matched nothing), proceed but note the context gap in Open Questions
