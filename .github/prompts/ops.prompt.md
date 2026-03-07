---
mode: agent
description: Infrastructure review, deployment checklist, or runbook generation
---

Read and follow the instructions in `cortex/commands/ops.md` exactly.

Detect mode from the input:
- Spec file attached → Mode A (infrastructure review)
- `deploy` keyword → Mode B (deployment checklist)
- `runbook` keyword → Mode C (runbook generation)

Always pull platform context from the knowledge base before generating output.
Never hardcode assumptions about the tech stack — query first.
