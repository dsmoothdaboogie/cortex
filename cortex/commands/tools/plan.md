# /plan

Break an epic or business goal into features, user stories, and spec candidates.

## When to use
When you have a business objective, epic, or rough idea and need to decompose it
before writing individual specs. Works with anything from a sentence to a full brief.

## Inputs
- An epic description — any length, any level of detail

## Steps

1. Load context:
   - List `cortex/knowledge/standards/` — read the 1–2 files most relevant to this epic's domain
   - Read `cortex/knowledge/vision/` — read vision files to ground feature decomposition in product direction
   - Read all files in `cortex/knowledge/team-conventions/` (if any exist)
   - If `.cortex-repos.json` is non-empty, also run:
     ```
     python3 cortex.py ask "{epic summary}" --top-k 5 --context-only
     ```
2. Understand what the team already has — components, patterns, decisions, and product direction
3. Decompose into features and user stories — grounded in what standards and past decisions require
4. Identify which features need specs and suggest ticket formats

## Output Format

```
# Plan — {Epic Title}

## Understanding
What you've inferred from the requirement + what the knowledge base confirms already exists.

## Features
Numbered list of discrete features.

## User Stories
For each feature:
  As a {role}, I want {goal} so that {benefit}.

## Spec Candidates
Ready-to-run commands for each feature that needs a spec:

  python3 cortex.py spec {TICKET}-{n} "{feature title}"
  → or in Copilot Chat: /spec {TICKET}-{n} "{feature title}"

## Dependencies
Features that must be built before others.

## Open Questions
Anything that needs product/design/arch input before spec creation.
```

## Rules
- Apply any rules from `--tag team-conventions` results — these are validated corrections that override generic inference
- Ground every feature in what the team's knowledge base already supports
- If knowledge files are missing, note which areas lacked coverage and proceed — check `cortex/specs/` directly for existing specs if needed
- Flag features that require new design system components or ADRs
- Don't create spec candidates for features that are already specced
