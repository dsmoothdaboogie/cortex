Read and follow the instructions in `cortex/commands/4-review.md` exactly.

Arguments: $ARGUMENTS

Detect what's being reviewed from context:
- File in `cortex/specs/` → run spec review
- File in `src/` or similar → run code review
- `--security` mentioned → add security review
- `--all` mentioned → chain spec + code + security

Before reviewing, always run the cortex queries defined in `cortex/commands/4-review.md`.
