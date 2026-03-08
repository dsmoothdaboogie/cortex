# /vision

Onboard a project with business intelligence by generating structured vision documents into `cortex/knowledge/vision/`.

## When to use
- At the start of a new project to capture product context before writing specs
- When joining an existing project that lacks documented vision
- When product strategy has shifted and the knowledge base needs updating

## Inputs
- A business brief — any length, any format (bullet points, paragraphs, stakeholder notes, PRD excerpt)
- Optional flag: `--update` to explicitly signal an update — preserves existing content that the new brief doesn't contradict

## What gets generated

Four files in `cortex/knowledge/vision/`:

| File | Contents |
|------|----------|
| `mission.md` | What the product is, why it exists, guiding principles |
| `personas.md` | Who uses it — roles, goals, pain points, success criteria |
| `capabilities.md` | What the platform does — current capabilities and differentiators |
| `product-plan.md` | Priorities, milestones, and what's next |

## Steps

1. Always check what already exists first:
   ```
   python3 cortex.py ask "product mission vision principles" --tag vision --context-only
   python3 cortex.py ask "platform decisions architecture" --tag adr --context-only
   ```

2. Analyse the input brief. Extract:
   - The product's purpose and the problem it solves
   - Who the users are and what they need
   - What the platform currently does or is planned to do
   - Priorities, goals, and known constraints

3. Generate each file using the templates below.

4. Save all four files to `cortex/knowledge/vision/`.

5. Ingest:
   ```
   python3 cortex.py add cortex/knowledge/vision --tag vision --force
   ```

6. Confirm what was created and suggest next steps.

---

## Templates

### mission.md

```markdown
# Mission

**Product:** {product name}
**Updated:** {YYYY-MM-DD}

## Purpose
One paragraph — what this product is and the core problem it solves.

## Mission Statement
A single sentence: We exist to {verb} {who} so they can {outcome}.

## Guiding Principles
- {Principle 1} — brief explanation
- {Principle 2} — brief explanation
- {Principle 3} — brief explanation

## Success Looks Like
What does "this is working" mean for users and for the business?
```

---

### personas.md

```markdown
# Personas

**Updated:** {YYYY-MM-DD}

## {Persona Name} — {Role Title}

**Who they are:** {1–2 sentence description}

**Primary goals:**
- {goal 1}
- {goal 2}

**Pain points:**
- {pain 1}
- {pain 2}

**Success criteria:**
{What does a great day look like for this person with this product?}

---

(Repeat for each persona)
```

---

### capabilities.md

```markdown
# Platform Capabilities

**Updated:** {YYYY-MM-DD}

## What the Platform Does
High-level summary of the platform's core function.

## Core Capabilities

### {Capability Area 1}
- {capability}
- {capability}

### {Capability Area 2}
- {capability}
- {capability}

## Differentiators
What makes this platform distinct from alternatives or competitors.

## Current Limitations
Known gaps or constraints that inform what we don't yet support.
```

---

### product-plan.md

```markdown
# Product Plan

**Updated:** {YYYY-MM-DD}

## Now — Current Focus
What the team is actively building or shipping.

## Next — Committed Pipeline
Features and improvements planned for the next cycle.

## Later — Backlog Intent
Strategic initiatives without committed timelines.

## Known Constraints
Technical, resource, or business constraints that shape the plan.

## Open Questions
Decisions that need to be made before planning can progress.
```

---

## Rules
- Derive everything from the input brief — never invent capabilities or personas not implied by the input
- If the brief is thin on a section, write what you can and flag it as needing input rather than fabricating
- Keep each file scannable — these are reference documents, not essays
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), skip the pre-check queries and read `cortex/knowledge/vision/` directly to check for existing content. Skip the ingest step — note that the DB is unavailable and the generated files should be ingested manually once the environment is active
- After generating, always ingest immediately so agents can query the vision
- If `--update` is used, preserve any existing content that the new brief doesn't contradict
