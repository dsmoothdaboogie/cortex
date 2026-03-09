# /ask

Search the knowledge base for relevant context.

## When to use
- When you need to search across **linked repos** (`.cortex-repos.json` is non-empty)
- For ad-hoc queries against the current repo's knowledge files

## Inputs
- A natural language query — anything

## Steps

1. Check `.cortex-repos.json`:
   - **Non-empty** → run a DB query to search across linked repos:
     ```
     python3 cortex.py ask "{query}" --top-k 5 --context-only
     ```
   - **Empty** → read local knowledge files directly (faster, no DB needed):
     - Check `cortex/knowledge/standards/STANDARDS.md` — synthesised standards summary
     - Check `cortex/knowledge/vision/VISION.md` — synthesised vision summary
     - Check `cortex/knowledge/adrs/ADR-INDEX.md` — synthesised ADR index
     - Then read individual files in the subfolder most relevant to the query topic

2. Summarise what the knowledge says and answer the question.
3. If nothing relevant is found, say so clearly — don't invent patterns.

## Useful folder map

| You want to know | Read from |
|-----------------|-----------|
| Which DS component to use | `cortex/knowledge/design-system/` |
| How to structure a feature | `cortex/knowledge/patterns/` |
| What was decided about X | `cortex/knowledge/adrs/` |
| What the standard is | `cortex/knowledge/standards/` |
| How the MFE platform works | `cortex/knowledge/standards/` + `adrs/` |
| Team conventions | `cortex/knowledge/team-conventions/` |

## Rules
- Never answer from assumptions — always read knowledge files first
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), fall back to reading `cortex/knowledge/` files directly — check `STANDARDS.md`, `VISION.md`, and `ADR-INDEX.md` first, then individual subfolder files relevant to the query topic
- If the knowledge base doesn't have relevant content, say so and suggest `/doc` to add it
