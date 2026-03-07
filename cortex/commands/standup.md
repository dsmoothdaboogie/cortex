# /standup

Summarise the current state of spec activity across the team.

## When to use
- Morning standup — what's in flight
- Sprint review prep
- Quick status check on a ticket

## Steps

1. Check spec sync status:
   ```
   python cortex.py ls --specs
   ```
2. Read the status field from each spec file
3. Pull recent context if a specific ticket is mentioned:
   ```
   python cortex.py ask "{ticket or feature}" --context-only
   ```
4. Summarise by status

## Output Format

```
## Standup — {date}

**In Progress**
- PROJ-1234 · auth flow redesign · [In Progress]

**In Review**
- PROJ-1230 · notification preferences · [Review]

**Blocked**
- PROJ-1229 · form migration · [Blocked] — open question: DS token availability

**Draft**
- PROJ-1235 · dashboard redesign · [Draft]

**Recently Done**
- PROJ-1228 · header web component · [Done]
```

## Rules
- Only report what the spec files actually say — don't invent status
- Flag stale specs (DB sync status = stale) as needing a sync
- If asked about a specific ticket, pull cortex context before answering
