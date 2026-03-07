---
mode: agent
description: Review a spec or code file against team standards
---

Read and follow the instructions in `commands/review.md` exactly.

Detect what's being reviewed from context:
- File in `specs/` → run spec review
- File in `src/` or similar → run code review
- `--security` mentioned → add security review
- `--all` mentioned → chain spec + code + security

Before reviewing, always run the cortex queries defined in `commands/review.md`.
