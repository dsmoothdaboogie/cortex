# /ops

Infrastructure review, deployment checklists, and runbook generation.

## When to use
- Before dev starts on a spec — catch infra implications early (Mode A)
- Before a release — generate a deployment checklist (Mode B)
- To document an operational process or incident response procedure (Mode C)

## Inputs
- Mode A (infra review): `#file:cortex/specs/PROJ-1234-feature.md`
- Mode B (deploy checklist): `deploy "release description"`
- Mode C (runbook): `runbook "incident or process description"`

## Mode detection
- Spec file attached → **Mode A**
- `deploy` keyword → **Mode B**
- `runbook` keyword → **Mode C**

---

## Mode A — Spec Infrastructure Review

Read the spec and flag any infrastructure or platform implications before development starts.

### Query the knowledge base
```bash
python cortex.py ask "deployment configuration platform infrastructure" --context-only
python cortex.py ask "platform architecture deployment" --context-only --tag standards
python cortex.py ask "infrastructure ADR {topic}" --context-only --tag adr
```

### Check for (pull from knowledge base first — apply what's documented for this team)
- New services or modules → check registration requirements
- New routes or endpoints → check routing config requirements
- New environment variables → check config management patterns
- Platform compatibility → browser, runtime, or environment constraints
- Feature flags → does this need a flag before full rollout?
- Service dependencies → potential deployment ordering issues
- Data persistence → storage namespace or conflict risks
- Performance → bundle size, lazy loading, or hydration concerns

### Output
```markdown
## Ops Review — {TICKET} {title}

### Infrastructure Implications
| Area | Impact | Action Required |
|------|--------|----------------|
| {area} | {impact} | {action or —} |

### Pre-Development Checklist
- [ ] {action before dev starts}

### Pre-Deployment Checklist
- [ ] {action before deploying}

### Risks
- {risk} → {mitigation}
```

> If no infrastructure implications exist, say so explicitly — "No infrastructure implications identified."

---

## Mode B — Deployment Checklist

Generate a deployment checklist for a release.

### Query the knowledge base
```bash
python cortex.py ask "deployment configuration platform" --context-only
python cortex.py ask "deployment ADR release" --context-only --tag adr
python cortex.py ask "deployment runbook process" --context-only --tag skills
python cortex.py ls --specs
```

### Output
```markdown
## Deployment Checklist — {release description}
**Date:** {date}
**Environment:** Staging → Production

### Pre-Deployment
- [ ] All specs status = Done
- [ ] `python cortex.py sync` — confirm DB is current
- [ ] Feature flags configured for gradual rollout
- [ ] Platform config reviewed for new routes or modules
- [ ] Environment variables confirmed in config
- [ ] Deployment order confirmed for interdependent services

### Deployment Steps
1. {ordered step}
2. {ordered step}

### Validation
- [ ] {smoke test}
- [ ] {monitoring check}

### Rollback Plan
{specific steps to revert — not just "revert the deploy"}
```

---

## Mode C — Runbook Generation

Generate a runbook for an operational process or incident response.

### Query the knowledge base
```bash
python cortex.py ask "ops runbook {process}" --context-only --tag skills
python cortex.py ask "{process} platform infrastructure" --context-only
```

### Output
```markdown
## Runbook — {process or incident type}

### When to use this runbook
{trigger conditions — be specific}

### Prerequisites
{what you need before starting}

### Steps
1. {step} — expected outcome: {outcome}
2. {step} — expected outcome: {outcome}

### Validation
{how to confirm it worked}

### Escalation
{when and who to escalate to}
```

> After writing a runbook, ingest it:
> ```bash
> python cortex.py add cortex/knowledge/skills/{slug}.md --tag skills --force
> ```

---

## Show what ran
```
Commands run:
  python cortex.py ask "deployment platform infrastructure" --context-only
  python cortex.py ask "infrastructure ADR" --context-only --tag adr
```

## Rules
- Infrastructure implications section is mandatory for every spec review — even if the answer is "no implications"
- Deployment checklists must be ordered — sequence matters
- Rollback plans must be specific — "revert the deploy" is not a plan
- Pull platform-specific requirements from the knowledge base — never hardcode assumptions about the stack
- If a platform concern exists but nothing is documented in the knowledge base, flag it as a knowledge gap and suggest running `@workspace /doc` to capture it
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), fall back to reading `cortex/knowledge/skills/` and `cortex/knowledge/standards/` directly — check for `STANDARDS.md` first. If cortex runs but returns no results (DB exists, query matched nothing), proceed but flag each output section as "unverified — no platform knowledge found" and recommend running `@workspace /doc` to capture platform context
