# Commands

Agent-agnostic command definitions. Each file contains the full instructions
for that command — what it does, how to do it, and what to output.

These files are the source of truth for all agent behaviour. Copilot Chat
prompt files in `.github/prompts/` point here. Devin reads these directly.

---

## Workflow

The four core steps — run these in order for every feature.

| File | Slash command | Purpose |
|------|--------------|---------|
| `1-vision.md` | `/vision` | Onboard a project with business intelligence — generate mission, personas, capabilities, and product plan |
| `2-spec.md` | `/spec` | Create a feature spec (any length of requirement) |
| `3-build.md` | `/build` | Generate implementation plan from a spec |
| `4-review.md` | `/review` | Review a spec or code file against team standards |

## Tools

Supporting commands — use as needed at any stage.

| File | Slash command | Purpose |
|------|--------------|---------|
| `tools/plan.md` | `/plan` | Break an epic into features and spec candidates |
| `tools/doc.md` | `/doc` | Create or update a knowledge base entry or ADR |
| `tools/wiki.md` | `/wiki` | Create or update a deep, structured knowledge base reference entry |
| `tools/refactor.md` | `/refactor` | Analyse code against team standards, produce a P1/P2/P3 refactor plan |
| `tools/ops.md` | `/ops` | Infrastructure review, deployment checklist, or runbook generation |
| `tools/ask.md` | `/ask` | Search the knowledge base |
| `tools/standup.md` | `/standup` | Summarise current spec activity |
| `tools/learn.md` | `/learn` | Capture agent corrections from a task as reusable rules |
| `tools/merge.md` | `/merge` | Promote High-confidence corrections into the authoritative knowledge doc |

---

## How Commands Use cortex

Every command that needs team context calls the cortex CLI:

```bash
python3 cortex.py ask "{query}" --context-only           # general query
python3 cortex.py ask "{query}" --tag standards          # standards only
python3 cortex.py ask "{query}" --tag design-system      # DS components only
python3 cortex.py ask "{query}" --tag adr                # decisions only
python3 cortex.py ls --specs                             # current spec state
```

Commands never assume how the team does something. They always query first.

### Fallback when cortex is unavailable

First, distinguish the two cases:

- **Script fails for any reason** (import error, missing dependencies, venv not active, "No DB found", non-zero exit) → Fall back to files (see below).
- **"No results"** → DB exists but the query matched nothing. The DB answered correctly — do not fall back, just proceed with reduced context and note the gap.

**When falling back to files**, read in this priority order:

**1. Generated summary artifacts first** — these are the most useful single files:
```
cortex/knowledge/standards/STANDARDS.md   → synthesised standards summary
cortex/knowledge/vision/VISION.md         → synthesised vision summary
cortex/knowledge/adrs/ADR-INDEX.md        → synthesised ADR index
```
If these exist, read the relevant one(s) before diving into individual files.

**2. Individual knowledge files** — for topic-specific depth:
```
cortex/knowledge/standards/       → coding standards and rules
cortex/knowledge/design-system/   → design system components and tokens
cortex/knowledge/adrs/            → architecture decisions
cortex/knowledge/patterns/        → implementation patterns
cortex/knowledge/team-conventions/ → team norms and process
cortex/knowledge/vision/          → product vision and personas
```

**3. Recent specs** — for prior decisions and established patterns:
```
cortex/specs/                     → previous feature specs (check dates — most recent first)
```

Read the files most relevant to the current task. Do not read everything — prioritise by folder name match to the topic at hand. The DB is a query accelerator — the markdown files are the source of truth and are always available in the workspace.

---

## Workflow Chain

```
/vision    →  business intelligence ingested into cortex/knowledge/vision/
/plan      →  epic broken into features + spec candidates
/spec      →  spec created, ingested into DB
/ops       →  infra review before dev starts (Mode A)
/review    →  verdict: READY / NEEDS WORK / BLOCKED
/build     →  implementation tasks (only after READY)
[code]
/review    →  code review against standards
/refactor  →  standards audit on existing code, P1/P2/P3 plan
/doc       →  quick knowledge capture (patterns, ADRs)
/wiki      →  deep reference documentation on a topic
/ops       →  deployment checklist (Mode B) or runbook (Mode C)
/learn     →  capture any agent corrections from the task as reusable rules
/merge     →  promote High-confidence corrections into the authoritative knowledge doc (quarterly)
```
