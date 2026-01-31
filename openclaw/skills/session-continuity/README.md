# Session Continuity

Never lose context to compaction again.

## The Problem

AI agents hit context limits. When they compact, they lose critical details — what you were working on, decisions made, next steps. You end up re-explaining everything.

## The Solution

Proactive state management. Don't wait for compaction — maintain a live state file that's **always current**.

```
state/current.md → Single source of truth
```

When compaction hits, the agent reads this file and picks up exactly where it left off.

## How It Works

1. **During tasks:** Agent updates `state/current.md` at every milestone
2. **Pre-compaction:** System prompts agent to write detailed handoff (~20k tokens before limit)
3. **After restart:** Agent reads state file FIRST, resumes seamlessly

## Setup

### 1. Create state directory

```bash
mkdir -p ~/workspace/state/checkpoints
```

### 2. Enable pre-compaction flush

Add to your `openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": {
          "enabled": true
        }
      }
    }
  }
}
```

### 3. Add to AGENTS.md

```markdown
### Session Continuity

**After ANY session restart:**
1. Read `state/current.md` FIRST
2. Resume active task if exists

**During tasks:**
- Update `state/current.md` at every milestone
- Don't wait for compaction
```

## State File Format

```markdown
# Current State
Updated: 2026-01-31 10:30 EST

## Active Task
**What:** Refactoring auth module
**Status:** in-progress

## Context
- Using OAuth 2.0 with PKCE
- Target: reduce token refresh latency

## Progress
- [x] Audit current implementation
- [x] Design new flow
- [ ] Implement changes (IN PROGRESS)

## Next Actions
1. Update token refresh logic
2. Add PKCE support
```

## Commands

| Phrase | Action |
|--------|--------|
| "checkpoint" | Create timestamped snapshot |
| "what's my state?" | Read current.md |
| "clear state" | Archive and start fresh |

## Why This Works

- **File-based:** Survives any restart, compaction, or crash
- **Always current:** Updated proactively, not reactively
- **Human-readable:** You can read/edit the state file yourself
- **Works with existing memory:** Complements daily notes and MEMORY.md

## Credits

Based on community patterns from:
- Bookend/MARVIN approach
- OpenClaw GitHub discussions
- r/openclaw community

## License

MIT
