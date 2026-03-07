---
mode: agent
description: Create or update a deep wiki entry in the knowledge base
---

Read and follow the instructions in `commands/wiki.md` exactly.

Detect mode from context:
- `update` keyword or `#file:` pointing to an existing knowledge file → update mode
- Otherwise → create mode

Always query cortex at top-k 8 before writing. Always ingest after saving.
