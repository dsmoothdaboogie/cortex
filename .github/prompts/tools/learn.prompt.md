---
mode: agent
description: Capture agent corrections from this task as reusable rules in the knowledge base
---

Read and follow the instructions in `cortex/commands/tools/learn.md` exactly.

Parse TOPIC and SECTION from the user's message. Ask if not provided.
Review the current conversation for corrections the user made to the agent's output.
Produce one structured entry per correction and append to the knowledge base.
Always ingest after saving.
