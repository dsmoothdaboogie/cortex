---
mode: agent
description: Promote High-confidence agent corrections into the authoritative knowledge doc
---

Read and follow the instructions in `cortex/commands/tools/merge.md` exactly.

Parse --learnings <file> and --into <file> from the user's message.
Parse optional --section <name> if provided.
Only merge High-confidence entries. Always re-ingest both files after saving.
