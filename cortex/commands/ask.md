# /ask

Search the knowledge base for relevant context.

## When to use
Any time you need to know how this team does something before writing code,
a spec, or documentation. Ask before assuming.

## Inputs
- A natural language query — anything

## Steps

1. Run: `python3 cortex.py ask "{query}" --context-only`
2. Read the results. Scores above 0.85 are strong matches.
3. If results are weak (below 0.70), try a different angle:
   ```
   python3 cortex.py ask "{query}" --tag standards --context-only
   python3 cortex.py ask "{query}" --tag design-system --context-only
   python3 cortex.py ask "{query}" --tag patterns --context-only
   ```
4. Summarise what the knowledge base says and answer the question.
5. If nothing relevant is found, say so clearly — don't invent patterns.

## Useful query patterns

| You want to know | Query |
|-----------------|-------|
| Which DS component to use | `"design system {element type}"` |
| How to structure a feature | `"patterns {feature domain}"` |
| What was decided about X | `"decision {topic}" --tag adr` |
| What the standard is | `"standards {domain}" --tag standards` |
| How the MFE platform works | `"MFE {topic}"` |
| Team conventions | `"{topic}" --tag team-conventions` |

## Rules
- Never answer from assumptions — always run the query first
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), fall back to reading `cortex/knowledge/` files directly — check `STANDARDS.md`, `VISION.md`, and `ADR-INDEX.md` first, then individual subfolder files relevant to the query topic
- If the knowledge base doesn't have relevant content, say so and suggest `/doc` to add it
- Scores below 0.60 are likely irrelevant — don't use them
