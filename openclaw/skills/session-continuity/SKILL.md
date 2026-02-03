---
name: session-continuity
description: Never lose context to compaction. Proactive state management that survives any session reset, compaction, or context overflow. Combines state files with Beads task tracking for bulletproof continuity.
---

# Session Continuity Skill

**Problem:** Context compaction and session resets cause agents to "forget" what they were working on. Compaction summaries lose critical details.

**Solution:** Two-layer persistence:
1. **State file** (`state/current.md`) — Human-readable current context
2. **Beads** (`.beads/`) — Structured, queryable task database

## Why Two Layers?

| Layer | Purpose | When to Use |
|-------|---------|-------------|
| `state/current.md` | "What am I doing RIGHT NOW?" | High-level context, prose |
| `bd list` | "What tasks are open?" | Granular task tracking |
| `memory/YYYY-MM-DD.md` | "What happened today?" | Append-only journal |

After compaction, the agent reads the state file for context AND runs `bd list` for the structured task queue. Belt and suspenders.

## Quick Start

### 1. Install Beads (one-time)

```bash
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
```

### 2. Initialize in your workspace

```bash
cd ~/your-agent-workspace
bd init
mkdir -p state
```

### 3. Add to AGENTS.md

```markdown
### 🔄 Session Continuity (CRITICAL)

**After ANY session start (including compaction):**
1. Read `state/current.md` FIRST
2. Run `bd list` to see open tasks
3. Resume active task if exists

**During work:**
- Update state/current.md at every milestone
- Create beads: `bd create "Task name"`
- Close beads when done: `bd close <id>`

**Before ending session:**
- Update state/current.md
- Run `bd sync` then `git push`
```

## Files

| File | Purpose |
|------|---------|
| `state/current.md` | Single source of truth — what you're working on RIGHT NOW |
| `state/checkpoints/` | Timestamped snapshots (auto-created) |
| `memory/YYYY-MM-DD.md` | Daily logs (existing OpenClaw pattern) |
| `.beads/beads.db` | Structured task database (survives compaction) |

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

## Beads — Structured Task Persistence

Beads provides a queryable SQLite database for task tracking that survives compaction.

### Key Commands

```bash
bd list                    # See all open tasks
bd create "Task name"      # Create a task
bd close <id>              # Mark complete
bd show <id>               # View details
bd epic create "Name"      # Group related tasks
bd sync                    # Sync with git (run before push)
```

### Post-Compaction Recovery

After compaction, run `bd list` FIRST. This gives you the structured task queue even when context is gone.

## Session Start Protocol

**EVERY session start (including after compaction):**

1. **Read state file FIRST:**
   ```
   Read state/current.md
   ```

2. **Query Beads for open tasks:**
   ```bash
   bd list
   ```

3. **Check for active task:**
   - If active task exists → Resume it
   - If no active task → Ready for new work

4. **Greet with context:**
   ```
   "Picking up where we left off: [task summary]. Open beads: [count]. Ready to continue?"
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

## Checkpoint Command

When user says "checkpoint" or "save state":

```bash
# Create timestamped checkpoint
cp state/current.md state/checkpoints/$(date +%Y%m%d-%H%M%S).md
```

Then confirm: "Checkpointed. Current state saved."

## Recovery Protocol

If state file is missing or corrupted:

1. Run `bd list` — Beads may have the task queue
2. Check `state/checkpoints/` for most recent
3. Check `memory/YYYY-MM-DD.md` for today's logs  
4. Use `memory_recall` to search for recent context
5. Ask user: "I don't have a current state file. What were we working on?"

## Integration with Existing Systems

### The Full Stack (No Conflicts)

| System | Purpose | Query Type |
|--------|---------|------------|
| **LanceDB** | Vector memory search | "What did we discuss about X?" (semantic) |
| **Beads** | Structured task tracking | "What tasks are open?" (explicit) |
| **state/current.md** | Current task context | "What am I doing RIGHT NOW?" (prose) |
| **memory/YYYY-MM-DD.md** | Daily logs | "What happened today?" (journal) |
| **MEMORY.md** | Long-term curated | "What matters long-term?" (curated) |

**Why no conflicts:**
- LanceDB = semantic recall (embeddings, similarity search)
- Beads = structured task state (SQLite queries)
- State file = human-readable context

They operate on different data types for different purposes. Use all three.

### Works WITH (not replacing):
- `memory/YYYY-MM-DD.md` — Daily logs (append-only journal)
- `MEMORY.md` — Long-term curated memory
- Pre-compaction flush — Still useful as backup
- LanceDB/memory_recall — Semantic search across all memory

## Config Recommendations

Ensure these are enabled in `openclaw.json`:

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

## Example Workflow

### Starting a Task
```
User: "Help me refactor the auth module"

Agent:
1. Run: bd create "Refactor auth module"
2. Create/update state/current.md with context
3. Begin work
4. Update state at each milestone
5. When done: bd close <id>
```

### After Compaction
```
[Compaction happens — context summarized]

Agent:
1. Reads state/current.md
2. Runs bd list — sees "Refactor auth module" is open
3. Says: "Picking up the auth refactor. We completed X, Y, Z. Now working on step 4."
4. Continues seamlessly
```

### End of Session
```
Agent:
1. Update state/current.md with final status
2. Close completed beads
3. Run bd sync
4. git push (if workspace is a repo)
5. Update memory/YYYY-MM-DD.md with summary
```

## Commands

| Phrase | Action |
|--------|--------|
| "checkpoint" / "save state" | Create timestamped checkpoint |
| "what's my state?" | Read state/current.md + bd list |
| "clear state" | Archive current.md, start fresh |
| "restore checkpoint" | List and restore from checkpoint |

## Anti-Patterns (Don't Do This)

❌ **Waiting for compaction** — Update state BEFORE context fills up
❌ **Relying on compaction summaries** — They lose detail
❌ **Mental notes** — If it matters, write it to state file or create a bead
❌ **Huge state files** — Keep current.md focused (under 500 words)
❌ **Duplicating daily logs** — State ≠ journal; state is CURRENT
❌ **Forgetting bd sync** — Always sync before ending session

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
- Beads by Steve Yegge
- OpenClaw pre-compaction flush
- GitHub Issue #2597 (context visibility)
- GitHub Issue #5429 (silent compaction data loss)
- r/ClaudeAI and r/LocalLLM community discussions
