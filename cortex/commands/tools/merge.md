# /merge

Promote High-confidence agent corrections from a learnings file into the authoritative knowledge doc.

## When to use
When a correction entry in a learnings file has:
- `Confidence: High`
- Appeared in 2 or more separate entries (look for repeated Section values)
- Been in the learnings file for 30+ days (enough time to validate in practice)

Do not merge Low or Medium confidence entries — keep them in the learnings file until confidence grows.

## Inputs
- `--learnings <file>` — the learnings file (e.g. `cortex/knowledge/team-conventions/design-system-learnings.md`)
- `--into <file>` — the target knowledge doc to update (e.g. `cortex/knowledge/design-system/button.md`)
- Optional: `--section <name>` — target a specific named section within the doc

## Steps

1. Read the learnings file (`--learnings`). Identify all entries where `Confidence: High` that do not already have a `Merged:` line.
   - If no High-confidence unmerged entries exist, report this and stop.
   - If entries exist but appear only once, flag them as "not yet ready — seen once, validate further"

2. Read the target knowledge doc (`--into`). If `--section` was provided, focus on that section; otherwise read the full doc.

3. For each High-confidence entry to merge, rewrite the relevant section of the target doc:
   - **Write as if the correction were always true** — no "Note:", "Correction:", "Previously:", or change attribution
   - Preserve all accurate existing content — only add, adjust, or clarify based on the correction
   - If existing content is wrong or misleading per the correction, fix it directly
   - If the correction documents previously undocumented behavior, add it naturally to the section
   - Match the existing tone, format, and heading structure exactly
   - If the correction contradicts other well-documented standards, **do not merge** — flag it for human review instead

4. Save the rewritten knowledge doc (same path as `--into`)

5. Re-ingest the knowledge doc with its original tag:
   ```
   python3 cortex.py add {--into path} --tag {original-tag} --force
   ```
   Determine the original tag from the file's `**Category:**` field, or infer from the folder:
   - `cortex/knowledge/standards/` → `standards`
   - `cortex/knowledge/design-system/` → `design-system`
   - `cortex/knowledge/patterns/` → `patterns`
   - `cortex/knowledge/adrs/` → `adr`
   - `cortex/knowledge/vision/` → `vision`
   - `cortex/knowledge/skills/` → `skills`
   - `cortex/knowledge/team-conventions/` → `team-conventions`

6. In the learnings file, mark each merged entry by adding `Merged: {YYYY-MM-DD}` on a new line after `Confidence:`. Do not delete the entries — they remain as an audit trail.

7. Re-ingest the updated learnings file:
   ```
   python3 cortex.py add {--learnings path} --tag team-conventions --force
   ```

8. Confirm: print which entries were merged, which were skipped and why, and the paths of both re-ingested files.

## Output

```
## Merge Summary — {date}

### Merged
- [{Section}] → {--into file}
  Rule baked in: "{Rule text}"

### Skipped
- [{Section}] Confidence: Medium — not ready to merge
- [{Section}] Contradicts {other-standard} — flagged for human review

### Files updated
- {--into path} (re-ingested as --tag {tag})
- {--learnings path} (entries marked Merged, re-ingested)
```

## Rules
- Only merge `Confidence: High` entries — Medium and Low stay in the learnings file
- Never remove accurate content from the target doc — only add or clarify
- If the correction reveals the entire target section is wrong, rewrite it but add a `> ⚠ Human review recommended — full section rewritten based on correction` callout above the section before ingesting
- One merge run should handle all eligible entries for a given learnings file — don't require running merge once per entry
- If `cortex ask` fails, proceed — the merge doesn't depend on the DB, only on reading and writing the files. Skip ingest steps and note they need to be run manually
