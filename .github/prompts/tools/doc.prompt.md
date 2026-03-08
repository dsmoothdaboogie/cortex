---
mode: agent
description: Create or update a knowledge base entry or ADR
---

Read and follow the instructions in `cortex/commands/tools/doc.md` exactly.

Detect the mode from context:
- `--adr` or "decision" language → write an ADR
- `--update <file>` → update existing entry
- Otherwise → new wiki entry

Always check for existing similar content with cortex before creating new entries.
Always ingest the file after saving.
