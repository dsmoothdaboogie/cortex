# /learn

Capture agent corrections from this task as reusable rules in the knowledge base.

## When to use
After completing any task where you corrected the agent's output. Run before closing the thread so the learning isn't lost.

Works for: design systems, API integrations, workflow conventions, prompt patterns, coding standards — any domain where agents make repeated mistakes.

## Inputs
- `TOPIC` — the domain these corrections belong to (e.g. `Design System`, `Cortex Workflow`, `API Patterns`, `Coding Standards`)
- `SECTION` — the specific area within that topic (e.g. `Button Component`, `Spec Format`, `Auth Patterns`)
- Optional: `--file <path>` to append to a specific knowledge file instead of the default

## Steps

1. Check for an existing learnings file for this topic:
   ```
   python3 cortex.py ask "{TOPIC} agent corrections learnings rules" --tag team-conventions --context-only
   ```
2. Review the current conversation thread for corrections — messages where the user changed, rejected, or overrode the agent's output
3. For each correction relevant to TOPIC and SECTION, produce one structured entry in this exact format:
   ```
   ---
   Date: {YYYY-MM-DD}
   Topic: {TOPIC}
   Section: {SECTION}
   Context: {one sentence describing the task and what was being built}

   Wrong pattern:
   {the incorrect code, config, or approach the agent produced — verbatim if possible}

   Correct pattern:
   {the correct version — verbatim if possible}

   Why: {one sentence explaining the reasoning — not just what changed, but why the correct pattern is right}

   Rule: {a generalized, reusable principle. Write it cold — no thread context assumed. Start with an action verb: "Always...", "Never...", "When X, use Y instead of Z..."}

   Confidence: Low | Medium | High
   Source: {brief task description or ticket ID}
   ---
   ```
4. Determine save path:
   - Default: `cortex/knowledge/team-conventions/{topic-slug}-learnings.md` (slugify TOPIC: lowercase, hyphens)
   - Or `--file <path>` if provided
5. If the file exists — append each new entry below the last `---` separator
   If the file is new — create it with this header, then append entries:
   ```markdown
   # Agent Learnings — {TOPIC}

   **Category:** team-conventions
   **Updated:** {YYYY-MM-DD}

   Correction entries captured from task threads. Each entry is one agent mistake and its corrected pattern.
   Use these when prompting agents on tasks in this domain.

   ```
6. Ingest: `python3 cortex.py add {path} --tag team-conventions --force`
7. Confirm the file was saved and ingested — print the path and number of entries added

## Rules for producing entries
- Only capture corrections where the agent was demonstrably wrong about TOPIC — not logic errors, off-topic fixes, or subjective style choices
- One entry per correction — never merge multiple corrections into one rule
- Write the Rule field so a future agent with no thread context can apply it immediately
- Confidence: Low = ambiguous or minor fix; Medium = clear pattern; High = rule seen 2+ times across tasks
- If there are no relevant corrections for the given TOPIC, say so explicitly — do not manufacture entries
- If `cortex ask` fails for any reason (script error, missing dependencies, "No DB found", or any non-zero exit), skip step 1 and check `cortex/knowledge/team-conventions/` directly for an existing file. Skip ingest and note it should be run manually once the environment is active
