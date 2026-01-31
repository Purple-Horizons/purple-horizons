# Sub-Agent Optimizer

Teaches AI agents to recognize parallelization opportunities AND audit/fix agent configs.

## Two Modes

### 1. Runtime Mode
Pattern recognition for parallelizable tasks. Agents learn to spawn sub-agents instead of processing sequentially.

**Triggers:** "Research these 5 items", "Create 3 variations", "For each X do Y"

### 2. Audit Mode  
Inspect agent configs, identify gaps in sub-agent permissions, suggest/apply fixes.

**Triggers:** "optimize agents", "audit agent config", "check subagent permissions"

## The Problem

1. **Sequential processing:** Agents do tasks one-by-one when they could parallelize
2. **Limited permissions:** Agents often can't spawn sub-agents (config not set up)

## The Solution

- Pattern recognition teaches agents WHEN to parallelize
- Audit mode checks configs and fixes permission gaps

## Audit Example

```
$ "audit agent config"

AUDIT RESULTS:

✅ orchestrator: Can spawn [content, research, sales] — Good
⚠️  content-agent: Can only spawn [main] — Limited
   → Recommend: Add [content, research]
⚠️  research-agent: Can only spawn [main] — Limited
   → Recommend: Add [research]
✅ sales-agent: Can spawn [sales, research, main] — Good

Apply recommended fixes? [y/n]
```

## Runtime Example

**Before:** 5 research tasks → 5 minutes sequential  
**After:** 5 workers in parallel → 1 minute

## Installation

```bash
# Copy to skills directory
cp -r subagent-optimizer ~/.openclaw/skills/
```

## Config Requirements

Agents need `subagents.allowAgents` in openclaw.json:

```json
{
  "id": "content-agent",
  "subagents": {
    "allowAgents": ["content-agent", "research-agent", "main"]
  }
}
```

## Best Practices

- Agents should be able to spawn themselves (parallel self-work)
- Research agents should be spawnable by others (delegation)
- Orchestrator should spawn all agent types
- Batch large spawns (5-8 at a time)

## License

MIT
