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

### Load context
- Read relevant files in `cortex/knowledge/standards/` (platform, architecture, deployment)
- Read relevant files in `cortex/knowledge/vision/` (product goals, constraints)
- Read relevant files in `cortex/knowledge/adrs/` (infrastructure decisions)
- If `.cortex-repos.json` is non-empty, also run:
  ```bash
  python3 cortex.py ask "{spec topic} infrastructure deployment" --top-k 5 --context-only
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

### Load context
- Read relevant files in `cortex/knowledge/standards/` (deployment, platform config)
- Read relevant files in `cortex/knowledge/skills/` (deployment runbooks, release process)
- Read relevant files in `cortex/knowledge/adrs/` (deployment decisions)
- Run: `python3 cortex.py ls --specs` — confirm all specs are Done before releasing
- If `.cortex-repos.json` is non-empty, also run:
  ```bash
  python3 cortex.py ask "deployment release" --top-k 5 --context-only
  ```

### Output
```markdown
## Deployment Checklist — {release description}
**Date:** {date}
**Environment:** Staging → Production

### Pre-Deployment
- [ ] All specs status = Done
- [ ] `python3 cortex.py sync` — confirm DB is current
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

### Load context
- Read relevant files in `cortex/knowledge/skills/` (existing runbooks and how-to patterns)
- Read relevant files in `cortex/knowledge/standards/` (platform infrastructure)
- If `.cortex-repos.json` is non-empty, also run:
  ```bash
  python3 cortex.py ask "{process} infrastructure" --top-k 5 --context-only
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
> python3 cortex.py add cortex/knowledge/skills/{slug}.md --tag skills --force
> ```

---

## Rules
- Infrastructure implications section is mandatory for every spec review — even if the answer is "no implications"
- Deployment checklists must be ordered — sequence matters
- Rollback plans must be specific — "revert the deploy" is not a plan
- Pull platform-specific requirements from the knowledge files — never hardcode assumptions about the stack
- If a platform concern exists but nothing is documented in `cortex/knowledge/`, flag it as a knowledge gap and suggest running `/doc` to capture it
- If knowledge files are missing or unreadable for a section, flag it as "unverified — no platform knowledge found" and recommend running `/doc` to capture platform context
