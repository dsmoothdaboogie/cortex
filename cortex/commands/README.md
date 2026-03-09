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

Commands read `cortex/knowledge/` markdown files **directly** — no DB query needed for the current repo. The DB is only queried when `.cortex-repos.json` is non-empty (cross-repo federation).

```
cortex/knowledge/standards/        → read 1–2 files relevant to the task domain
cortex/knowledge/design-system/    → read the file matching the feature's UI layer
cortex/knowledge/team-conventions/ → read all files (usually small)
cortex/knowledge/adrs/             → read for architectural context
cortex/knowledge/vision/           → read for product direction
cortex/knowledge/skills/           → read for how-to patterns
```

When `.cortex-repos.json` is non-empty, commands also run a single DB query to pull context from linked repos:
```bash
python3 cortex.py ask "{topic}" --top-k 5 --context-only
```

Commands never assume how the team does something. They always read the knowledge files first.

---

## Command Diagrams

### /vision — reads and writes `cortex/knowledge/vision/`

```mermaid
flowchart LR
  input([Business Brief]) --> vision[/vision]
  vision -->|reads existing| KV[knowledge/vision/]
  vision -->|writes| M[mission.md]
  vision -->|writes| P[personas.md]
  vision -->|writes| C[capabilities.md]
  vision -->|writes| PP[product-plan.md]
  M & P & C & PP --> ingest[(DB — publish for other repos)]
  KR[.cortex-repos.json non-empty] -.->|optional cross-repo query| DB2[(Linked repo DB)]
```

### /spec — reads standards, design-system, team-conventions

```mermaid
flowchart LR
  input([Ticket + Requirement]) --> spec[/spec]
  spec -->|reads 1-2 relevant| KS[knowledge/standards/]
  spec -->|reads 1 relevant| KD[knowledge/design-system/]
  spec -->|reads all| KT[knowledge/team-conventions/]
  spec -->|writes| SF[specs/TICKET/spec.md]
  SF --> ingest[(DB — publish for other repos)]
  KR[.cortex-repos.json non-empty] -.->|optional cross-repo query| DB2[(Linked repo DB)]
```

### /build — reads standards, team-conventions

```mermaid
flowchart LR
  input([spec.md READY]) --> build[/build]
  build -->|reads spec| SF[specs/TICKET/spec.md]
  build -->|reads 1-2 relevant| KS[knowledge/standards/]
  build -->|reads all| KT[knowledge/team-conventions/]
  build -->|writes| PF[specs/TICKET/plan.md]
  PF --> ingest[(DB — publish for other repos)]
  KR[.cortex-repos.json non-empty] -.->|optional cross-repo query| DB2[(Linked repo DB)]
```

### /review — reads standards, design-system, team-conventions

```mermaid
flowchart LR
  input([spec or code file]) --> review[/review]
  review -->|reads 1-2 relevant| KS[knowledge/standards/]
  review -->|spec: reads 1| KD[knowledge/design-system/]
  review -->|reads all| KT[knowledge/team-conventions/]
  review --> V[Verdict: READY / NEEDS WORK / BLOCKED]
  KR[.cortex-repos.json non-empty] -.->|optional cross-repo query| DB2[(Linked repo DB)]
```

---

### If the venv is unavailable

Skip the optional cross-repo DB query — direct file reads from `cortex/knowledge/` always work regardless of environment state. The generated summary artifacts are the fastest entry points:

```
cortex/knowledge/standards/STANDARDS.md   → synthesised standards summary
cortex/knowledge/vision/VISION.md         → synthesised vision summary
cortex/knowledge/adrs/ADR-INDEX.md        → synthesised ADR index
```

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
