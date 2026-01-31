---
name: session-continuity
description: Never lose context to compaction. Proactive state management that survives any session reset, compaction, or context overflow. Based on community patterns (Bookend, MARVIN) and Clawdbot architecture research.
---

# Session Continuity Skill

**Problem:** Context compaction and session resets cause agents to "forget" what they were working on. Compaction summaries lose critical details.

**Solution:** Proactive state file management. Don't wait for compaction — maintain a live state file that's ALWAYS current.

## Core Principle

> Your agent needs a "current state" file that's ALWAYS current. When compaction hits, it reads that file and picks up exactly where it left off.

## Files

| File | Purpose |
|------|---------|
| `state/current.md` | Single source of truth — what you're working on RIGHT NOW |
| `state/checkpoints/` | Timestamped snapshots (auto-created) |
| `memory/YYYY-MM-DD.md` | Daily logs (existing Clawdbot pattern) |

## State File Format

```markdown
# Current State
Updated: 2026-01-31 10:30 EST

## Active Task
**What:** [One-line description]
**Started:** [timestamp]
**Status:** [in-progress | blocked | waiting-for-user]

## Context
- [Key fact 1 needed to continue]
- [Key fact 2]
- [Key fact 3]

## Progress
- [x] Step completed
- [x] Another step
- [ ] Next step (IN PROGRESS)
- [ ] Future step

## Decisions Made
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

## Blockers
- [Blocker if any]

## Next Actions
1. [Immediate next step]
2. [After that]
```

## When to Update State

### ALWAYS Update When:
- Starting a new task
- Completing a milestone
- Making a decision
- Hitting a blocker
- User provides important context
- Before any long-running operation
- Every 30 minutes during active work

### Auto-Checkpoint Triggers:
- Task completion
- User says "remember this" or "don't forget"
- Before spawning sub-agents
- Before running commands that might timeout
- When context feels "heavy" (lots of back-and-forth)

## Session Start Protocol

**EVERY session start (including after compaction):**

1. **Read state file FIRST:**
   ```
   Read state/current.md
   ```

2. **Check for active task:**
   - If active task exists → Resume it
   - If no active task → Ready for new work

3. **Greet with context:**
   ```
   "Picking up where we left off: [task summary]. Last checkpoint was [time]. Ready to continue?"
   ```

## Checkpoint Command

When user says "checkpoint" or "save state":

```bash
# Create timestamped checkpoint
cp state/current.md state/checkpoints/$(date +%Y%m%d-%H%M%S).md
```

Then confirm: "Checkpointed. Current state saved."

## Recovery Protocol

If state file is missing or corrupted:

1. Check `state/checkpoints/` for most recent
2. Check `memory/YYYY-MM-DD.md` for today's logs  
3. Use `memory_recall` to search for recent context
4. Ask user: "I don't have a current state file. What were we working on?"

## Integration with Existing Systems

### Works WITH (not replacing):
- `memory/YYYY-MM-DD.md` — Daily logs (append-only journal)
- `MEMORY.md` — Long-term curated memory
- Pre-compaction flush — Still useful as backup

### Difference from Daily Memory:
- **Daily memory:** Raw logs of what happened
- **State file:** Live, always-current task state

## Config Recommendations

Ensure these are enabled in `clawdbot.json`:

```json
{
  "compaction": {
    "memoryFlush": { "enabled": true }
  },
  "agents": {
    "defaults": {
      "memorySearch": {
        "experimental": {
          "sessionMemory": true
        },
        "sources": ["memory", "sessions"]
      }
    }
  }
}
```

## AGENTS.md Integration

Add to your AGENTS.md:

```markdown
### 🔄 Session Continuity (CRITICAL)

**The Problem:** Sessions fill up, compact, and lose context.

**The Solution:** Maintain `state/current.md` — ALWAYS current.

**During tasks:**
- Update state/current.md at every milestone
- Checkpoint every 30 min during active work
- Don't wait for memory flush

**After ANY session start:**
1. Read state/current.md FIRST
2. Resume active task if exists
3. Confirm context with user

**State file location:** `state/current.md`
```

## Example Workflow

### Starting a Task
```
User: "Help me refactor the auth module"

Agent:
1. Create/update state/current.md:
   - Task: Refactor auth module
   - Status: in-progress
   - Context: [relevant details]
2. Begin work
3. Update state at each milestone
```

### After Compaction
```
[Compaction happens — context summarized]

Agent:
1. Reads state/current.md
2. Sees: "Refactoring auth module, completed steps 1-3, on step 4"
3. Says: "Picking up the auth refactor. We completed X, Y, Z. Now working on step 4."
4. Continues seamlessly
```

### End of Day
```
Agent:
1. Update state/current.md with final status
2. Create checkpoint
3. Update memory/YYYY-MM-DD.md with summary
4. Optionally update MEMORY.md with lessons learned
```

## Commands

| Phrase | Action |
|--------|--------|
| "checkpoint" / "save state" | Create timestamped checkpoint |
| "what's my state?" | Read and summarize current.md |
| "clear state" | Archive current.md, start fresh |
| "restore checkpoint" | List and restore from checkpoint |

## Anti-Patterns (Don't Do This)

❌ **Waiting for compaction** — Update state BEFORE context fills up
❌ **Relying on compaction summaries** — They lose detail
❌ **Mental notes** — If it matters, write it to state file
❌ **Huge state files** — Keep current.md focused (under 500 words)
❌ **Duplicating daily logs** — State ≠ journal; state is CURRENT

## Triggers

Use this skill when:
- Starting any multi-step task
- Session restarts unexpectedly
- User mentions "you forgot" or "we talked about this"
- After any `/new` or `/compact` command
- Resuming work after a break

## Credits

Based on community patterns:
- Bookend approach (MARVIN)
- Clawdbot pre-compaction flush
- GitHub Issue #2597 (context visibility)
- r/moltbot and r/clawdbot discussions
