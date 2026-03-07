# /build

Generate an implementation plan from a spec file.

## When to use
After a spec has passed `/review` with verdict READY. Do not build from an unreviewed spec.

## Inputs
- A spec file path (e.g. `cortex/specs/PROJ-1234-2025-01-15-auth-flow.md`)
- Optional flag: `--full` to also generate QA test plan and ops review

## Steps

1. Read the spec file
2. Pull implementation context:
   ```
   python cortex.py ask "{feature domain}" --context-only
   python cortex.py ask "{feature domain} standards" --tag standards --context-only
   python cortex.py ask "design system {component type}" --tag design-system --context-only
   python cortex.py ask "implementation patterns {feature domain}" --tag patterns --context-only
   python cortex.py ask "{feature domain} decisions" --tag adr --context-only
   ```
3. Generate the implementation plan (see format below)
4. If `--full`: also generate QA plan and ops review after the implementation plan

## Implementation Plan Format

```
# Implementation Plan — {TICKET}

## Summary
One paragraph: what's being built and the approach.

## Prerequisites
- [ ] Spec status is READY
- [ ] Any blocking tickets resolved
- [ ] Design system components available

## Tasks
Ordered list. Each task:
- ID: T-{n}
- Title
- Effort: XS / S / M / L
- AC refs: which spec AC items this covers
- Components: design system components used
- Notes: gotchas, decisions, patterns to follow

## Task List

### T-1 — {title} · {effort}
**AC:** #1, #2
**Components:** {DS components}
{implementation notes}

...

## Dependencies
Which tasks block which.

## Estimated Total Effort
{sum with breakdown}
```

## If --full also include:

### QA Plan
- Unit tests per AC item
- Integration test scenarios
- Accessibility checks
- Edge cases

### Ops Review
- Infrastructure or platform registration changes needed
- Route or config changes
- Environment variables
- Compatibility considerations (SSR, browser APIs, etc.)
- Pre-deployment checklist

## Rules
- Never create tasks without an AC reference
- Reference design system components by name where they exist — pull from `--tag design-system` before naming any component
- Flag any task that touches auth, shared state, or cross-system boundaries — these need explicit design
- If `cortex ask` returns "No DB found", fall back to reading `cortex/knowledge/` files directly — check `STANDARDS.md` and design-system files first, then recent specs for prior patterns. If cortex returns no results (DB exists, query matched nothing), proceed but flag ungrounded component references in task notes
