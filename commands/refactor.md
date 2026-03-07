# /refactor

Analyse existing code against current team standards and produce a prioritised refactor plan.

## When to use
- Before a migration or design system adoption sprint
- When code has grown organically and needs a standards audit
- To get a scope estimate before raising a refactor ticket
- After new standards are added and you want to identify gaps in existing code

## Inputs
- A file or folder reference: `#file:src/app/feature/`
- Optional goal string: `"prepare for design system migration"`

## Steps

### Step 1 — Read and inventory the code
Read all provided files. Build an internal inventory:
- Code types present (components, services, utilities, etc.)
- Patterns used — note anything that looks non-standard or inconsistent
- Design system adoption level (native UI elements vs design system components)
- State management approach
- Test coverage presence

### Step 2 — Query current standards
```bash
python cortex.py ask "{code domain} standards" --context-only --tag standards
python cortex.py ask "design system {components in file}" --context-only --tag design-system
python cortex.py ask "refactor patterns {domain}" --context-only --tag patterns
python cortex.py ask "{relevant decisions}" --context-only --tag adr
```

### Step 3 — Gap analysis
Compare inventory against standards. Categorise every gap:

- **P1 — Must Fix** — violates a hard standard or blocks other work
- **P2 — Should Fix** — degrades maintainability or creates inconsistency
- **P3 — Nice to Have** — modernisation or cleanup with no urgent driver

### Step 4 — Output the refactor plan

```markdown
## Refactor Plan — {files reviewed}
**Reviewed against:** knowledge/standards/ · knowledge/design-system/
**Date:** {date}

---

### Summary
| Priority | Count | Effort |
|----------|-------|--------|
| P1 Must Fix | {n} | {S/M/L} |
| P2 Should Fix | {n} | {S/M/L} |
| P3 Nice to Have | {n} | {S/M/L} |

---

### P1 — Must Fix

#### {Issue title}
- **File:** `{path}` line {n}
- **Problem:** {what's wrong}
- **Standard:** `knowledge/standards/{file}.md`
- **Fix:** {specific what to do}
- **Effort:** S / M / L

---

### P2 — Should Fix
{same format}

### P3 — Nice to Have
{same format}

---

### Suggested Next Step
{If scope is small: "These can be addressed inline."}
{If scope is large (> 5 L-effort items): "Recommend tracking this as a spec — run @workspace /spec {TICKET} 'refactor {description}'"}
```

### Step 5 — Show what ran
```
Commands run:
  python cortex.py ask "{domain} standards" --context-only --tag standards
  python cortex.py ask "design system {components}" --context-only --tag design-system
```

## Rules
- Every recommendation must cite a specific standard or ADR — no opinion-based suggestions
- Effort estimates: S = < 1hr, M = half day, L = full day+
- If the codebase has no violations, say so clearly — a clean bill of health is a valid output
- If the refactor scope is large (> 5 L-effort items), recommend breaking it into a tracked spec
- Never recommend rewriting something that works correctly and follows standards just because a newer pattern exists
- If `cortex ask` returns "No DB found", fall back to reading `knowledge/standards/STANDARDS.md` first, then individual files in `knowledge/standards/` and `knowledge/design-system/`. Every finding must cite a documented standard. If cortex returns no results (DB exists, query matched nothing), output only P3 items marked "unverified — no KB coverage" and recommend running `cortex audit` to identify gaps
