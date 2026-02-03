# session-continuity

**Never lose context to compaction again.**

An OpenClaw skill that combines proactive state files with structured task tracking to ensure your AI agent never forgets what it was working on — even after context compaction or session resets.

## The Problem

AI agents have a "context window" — essentially short-term memory. When it fills up, the agent compresses old messages (compaction) to make room. The problem?

- **Compaction summaries lose detail** — Critical context gets flattened
- **No warning before compaction** — Agent can't prepare
- **Silent data loss** — Agent wakes up with amnesia
- **No recovery path** — Agent doesn't know what it doesn't know

This is the #1 pain point in the OpenClaw/Claude Code community. Users report losing hours or even days of agent context to silent compaction.

## The Solution

Two-layer persistence that survives any compaction:

| Layer | What It Does | Format |
|-------|--------------|--------|
| **State File** | "What am I doing RIGHT NOW?" | Human-readable markdown |
| **Beads** | "What tasks are open?" | Queryable SQLite database |

After compaction, the agent reads both layers and immediately knows:
1. The high-level context (state file)
2. The granular task queue (Beads)

## Installation

### 1. Copy the skill to your OpenClaw skills directory

```bash
# Clone or download
git clone https://github.com/Purple-Horizons/purple-horizons.git
cp -r purple-horizons/openclaw/skills/session-continuity ~/.openclaw/skills/
```

### 2. Install Beads (optional but recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
```

### 3. Initialize in your workspace

```bash
cd ~/your-agent-workspace
bd init          # Initialize Beads
mkdir -p state   # Create state directory
```

### 4. Add to your AGENTS.md

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

## How It Works

### State File (`state/current.md`)

A human-readable markdown file that describes what the agent is currently doing:

```markdown
# Current State
Updated: 2026-01-31 10:30 EST

## Active Task
**What:** Refactoring the auth module
**Status:** in-progress

## Context
- Using OAuth 2.0 with PKCE
- Migrating from session-based to JWT
- User requested no breaking changes to existing API

## Progress
- [x] Analyzed current auth flow
- [x] Designed new JWT structure
- [ ] Implementing token refresh (IN PROGRESS)
- [ ] Update API documentation

## Next Actions
1. Complete token refresh implementation
2. Write tests for edge cases
```

### Beads (`.beads/`)

A structured task database that survives compaction:

```bash
$ bd list
┌─────────────┬─────────────────────────────────┬────────┐
│ ID          │ Title                           │ Status │
├─────────────┼─────────────────────────────────┼────────┤
│ proj-a3f2   │ Refactor auth module            │ open   │
│ proj-7b1c   │ Update API documentation        │ open   │
│ proj-9d4e   │ Write integration tests         │ open   │
└─────────────┴─────────────────────────────────┴────────┘
```

### Recovery Flow

When compaction happens:

1. Agent's context gets compressed
2. Agent reads `state/current.md` → Gets high-level context
3. Agent runs `bd list` → Gets structured task queue
4. Agent says: "Picking up where we left off: [task]. Open tasks: 3. Ready to continue?"
5. Work continues seamlessly

## Works With (No Conflicts)

This skill integrates cleanly with other memory systems:

| System | Purpose | This Skill's Role |
|--------|---------|-------------------|
| **LanceDB** | Semantic memory search | Complements — different query type |
| **memory_recall** | Find past discussions | Complements — different data |
| **memoryFlush** | Pre-compaction save | Works together — belt and suspenders |
| **Daily logs** | Journal of events | Different purpose — state ≠ journal |

## Configuration

Enable these in your `openclaw.json` for best results:

```json
{
  "compaction": {
    "memoryFlush": { 
      "enabled": true,
      "softThresholdTokens": 30000
    }
  }
}
```

## Key Commands

| Phrase | What It Does |
|--------|--------------|
| "checkpoint" | Creates timestamped backup of state file |
| "what's my state?" | Reads and summarizes current.md |
| "clear state" | Archives state file, starts fresh |
| `bd list` | Shows all open tasks |
| `bd create "..."` | Creates a new task |
| `bd close <id>` | Marks task complete |

## Anti-Patterns

❌ **Waiting for compaction** — Update state BEFORE context fills up  
❌ **Relying on compaction summaries** — They lose critical detail  
❌ **Mental notes** — If it matters, write it down  
❌ **Huge state files** — Keep it under 500 words  
❌ **Forgetting bd sync** — Always sync before ending session  

## Credits

Based on community patterns and research:

- **Bookend approach** (MARVIN pattern)
- **Beads** by Steve Yegge
- **GitHub Issue #2597** — Context visibility request
- **GitHub Issue #5429** — Silent compaction data loss
- **r/ClaudeAI** and **r/LocalLLM** community discussions

## Related

- [Beads](https://github.com/steveyegge/beads) — The underlying task persistence system
- [OpenClaw docs](https://docs.openclaw.ai) — Official documentation
- [subagent-optimizer](../subagent-optimizer) — Parallelize work with sub-agents
- [x-engagement](../x-engagement) — Auto-engage on X/Twitter

## License

MIT
