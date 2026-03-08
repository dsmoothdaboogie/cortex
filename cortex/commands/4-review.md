# /review

Review a spec or code file against team standards.

## When to use
- After writing a spec → pass a spec file to check completeness and standards alignment
- After writing code → pass a file or folder to check against coding standards
- When security concerns exist → add `--security` to the invocation

## Inputs
- A spec file, source file, or folder path
- Optional flag: `--security` to run security review
- Optional flag: `--all` to chain spec + code + security

## Steps

### Spec Review (file is in cortex/specs/)

1. Pull relevant standards:
   ```
   python3 cortex.py ask "{spec topic}" --context-only
   python3 cortex.py ask "{spec topic} product vision goals personas" --tag vision --context-only
   python3 cortex.py ask "{spec topic} standards" --tag standards --context-only
   python3 cortex.py ask "design system components" --tag design-system --context-only
   python3 cortex.py ask "{spec topic} decisions" --tag adr --context-only
   ```
2. Check every AC item — is it testable? Unambiguous?
3. Check Design System Usage — are component names real and in the knowledge base? No generic HTML elements where DS equivalents exist?
4. Check Technical Approach — does it align with `cortex/knowledge/standards/`?
5. Check for open auth, data handling, or cross-system concerns
6. Return verdict: **READY** / **NEEDS WORK** / **BLOCKED**
7. For NEEDS WORK or BLOCKED — list each issue with the section it appears in
8. If verdict is READY — update `**Status:**` in the spec file to `Review Passed`
   If verdict is BLOCKED — update `**Status:**` to `Blocked`

### Code Review (file is in src/ or similar)

1. Pull relevant standards:
   ```
   python3 cortex.py ask "{code domain}" --context-only
   python3 cortex.py ask "{code domain} standards" --tag standards --context-only
   python3 cortex.py ask "design system usage" --tag design-system --context-only
   python3 cortex.py ask "patterns {code domain}" --tag patterns --context-only
   python3 cortex.py ask "{code domain} decisions" --tag adr --context-only
   ```
2. Review against the pulled context — apply what the standards say, not generic rules
3. Return a table: | Line | Violation | Standard | Fix |
4. Flag violations against the pulled standards. Common categories: non-standard patterns, missing design system usage, unsafe types, styling violations, cross-system state concerns. Only flag what is documented in the knowledge base.

### Security Review (--security flag)

1. Pull security context:
   ```
   python3 cortex.py ask "security auth data handling" --context-only
   python3 cortex.py ask "security auth data handling" --tag standards --context-only
   ```
2. Check: auth requirements defined, input validation, data handling, sensitive data storage, cross-system surface
3. Return verdict: **CLEAR** / **REVIEW REQUIRED** / **BLOCKED**
4. List every finding with severity: HIGH / MEDIUM / LOW

## Output Format

**Spec review:**
```
Verdict: READY | NEEDS WORK | BLOCKED

Issues:
- [Section] Description of issue
```

**Code review:**
```
| Line | Violation | Standard | Fix |
|------|-----------|----------|-----|
```

**Security review:**
```
Verdict: CLEAR | REVIEW REQUIRED | BLOCKED

Findings:
- [HIGH/MEDIUM/LOW] Description
```

## Rules
- Only flag issues that are documented in the knowledge base — no generic or opinion-based feedback
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), fall back to reading `cortex/knowledge/` files directly — check `STANDARDS.md` and `ADR-INDEX.md` first, then individual files. Never issue a verdict without standards context. If cortex runs but returns no results (DB exists, query matched nothing), issue the verdict but flag which standards areas lacked KB coverage
