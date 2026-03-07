# /wiki

Create or update a deep wiki entry in the knowledge base.

## When to use
- When you need thorough, team-specific reference documentation on a topic
- When `/doc` is too lightweight — this is the long-form, comprehensive version
- When a pattern, system, or module needs a full explanation with examples and common mistakes
- To update an existing wiki entry with new information

## Difference from /doc
- `/doc` = quick capture (pattern discovered, ADR, runbook) — lightweight, fires after you learn something
- `/wiki` = deep reference page — queries at top-k 8, multi-angle, structured for developers who need to understand something fully

## Inputs
- A topic string: `"Module Federation setup"`
- Optional: `update #file:cortex/knowledge/patterns/form-patterns.md` to update an existing entry

## Steps

### Create mode (default)

1. Query the knowledge base deeply across multiple angles:
   ```bash
   python cortex.py ask "{topic}" --context-only --top-k 8
   python cortex.py ask "{topic} standards" --context-only --tag standards
   python cortex.py ask "{topic} ADR" --context-only --tag adr
   python cortex.py ask "{topic} patterns" --context-only --tag patterns
   ```

2. Check for an existing entry. If one exists, suggest `update` mode instead.

3. Determine the right location:

   | Topic type | Location |
   |-----------|----------|
   | Reusable how-to pattern | `cortex/knowledge/patterns/{slug}.md` |
   | Team convention or process | `cortex/knowledge/team-conventions/{slug}.md` |
   | Design system component deep-dive | `cortex/knowledge/design-system/{slug}.md` |
   | Skill / agent-consumable how-to | `cortex/knowledge/skills/{slug}.md` |
   | Standard or rule | `cortex/knowledge/standards/{slug}.md` |

4. Write the wiki entry (see template below).

5. Ingest:
   ```bash
   python cortex.py add cortex/knowledge/{folder}/{slug}.md --tag {tag} --force
   ```

### Update mode (`update #file:...`)

1. Read the existing file.
2. Pull current context: `python cortex.py ask "{topic}" --context-only --top-k 8`
3. Merge new information — preserve existing content, extend or correct sections.
4. Re-ingest: `python cortex.py add {file} --tag {tag} --force`

## Output template

```markdown
# {Title}

**Category:** {tag}
**Last Updated:** {YYYY-MM-DD}
**Related:** {links to related knowledge files}

---

## Overview

{What this is and why it matters to this team. 2-3 sentences.}

## How It Works

{Deep explanation. Use code examples from the actual codebase.}

## Usage

{How a developer uses this. Concrete examples.}

## Examples

{Real code or config examples. Reference actual team files where possible.}

## Common Mistakes

{What people get wrong. Specific, not generic.}

## Related Standards

{Which standards from cortex/knowledge/standards/ apply here}

## Related ADRs

{Which ADRs drove the decisions reflected in this document}

---
*Maintained by wiki-builder agent · cortex*
*Re-generate with: @workspace /wiki update #file:{this-file}*
```

## Show what ran

```
✓ Written: cortex/knowledge/{folder}/{slug}.md
✓ Ingested into knowledge base

Commands run:
  python cortex.py ask "{topic}" --context-only --top-k 8
  python cortex.py ask "{topic} standards" --context-only --tag standards
  python cortex.py add cortex/knowledge/{folder}/{slug}.md --tag {tag} --force
```

## Rules
- Every code example must use real team components and patterns, not generics
- If the knowledge base doesn't have enough context to write the entry accurately, say so explicitly — do not fill gaps with assumptions
- Always include the "Common Mistakes" section — this is often the most valuable part
- Related Standards and ADRs must cite actual files that exist in the knowledge base
- Wiki entries should be comprehensive but scannable — use headers, tables, and code blocks liberally
- If `cortex ask` returns "No DB found", fall back to reading `cortex/knowledge/` files directly — check `STANDARDS.md` and `ADR-INDEX.md` first, then individual subfolder files. Do not write an entry without grounding it in documented content. If cortex returns no results (DB exists, query matched nothing), state that the KB has no existing coverage on this topic and write the entry as a first document — flag it clearly
