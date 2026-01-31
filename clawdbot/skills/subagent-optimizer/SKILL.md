---
name: subagent-optimizer
description: Identify opportunities to parallelize work using sub-agents. Use when receiving multi-item tasks, batch operations, or work that could benefit from concurrent execution. Triggers on phrases like "research these 5 companies", "create 3 variations", "check all of these", or any task with multiple independent items.
---

# Sub-Agent Optimizer

Recognize when to spawn sub-agents for parallel execution instead of sequential work.

## The Decision Framework

**Spawn sub-agents when:**
- Task has multiple independent items (5 leads, 3 drafts, 10 links)
- Items don't depend on each other's results
- Time savings justify the overhead
- Each item takes >30 seconds of work

**Do it yourself when:**
- Items depend on previous results
- Only 1-2 items
- Task requires your accumulated context
- Coordination overhead exceeds time savings

## Pattern Recognition

### Immediate Spawn Triggers

| Pattern | Example | Action |
|---------|---------|--------|
| "Research these N companies" | "Research these 5 leads" | Spawn N scout workers |
| "Create N variations" | "Write 3 tweet options" | Spawn N content workers |
| "Check/verify all of X" | "Verify all 10 links work" | Spawn workers per batch |
| "For each X, do Y" | "For each competitor, analyze pricing" | Spawn per item |
| "In parallel" / "simultaneously" | "Research both simultaneously" | Explicit parallel request |

### Batch Sizing

- **Small batch (2-3 items):** Consider doing sequentially
- **Medium batch (4-10 items):** Spawn sub-agents
- **Large batch (10+ items):** Spawn in waves of 5-8 to avoid overwhelming

## Spawn Pattern

```python
# Standard parallel spawn
for item in items:
    sessions_spawn(
        agentId="scout",  # or self for same-type work
        task=f"[Specific task for {item}]. Return: [expected output format]."
    )

# With result aggregation
results = []
for item in items:
    sessions_spawn(
        agentId="scout",
        task=f"Research {item}. Return JSON: {{company, summary, decision_makers, score}}"
    )
# Results announce back → aggregate → deliver
```

## Sub-Agent Selection

| Task Type | Spawn Agent | Why |
|-----------|-------------|-----|
| Research, fact-finding | scout | Research-optimized |
| Content drafts, copy | rex (or self) | Voice-consistent |
| Lead research | scout | Deep research tools |
| Personalization at scale | self | Context-aware |

## Example Transformations

### Before (Sequential)
```
User: "Research Apple, Google, and Microsoft's AI strategies"
Agent: *researches Apple* ... *researches Google* ... *researches Microsoft*
Time: 3 minutes
```

### After (Parallel)
```
User: "Research Apple, Google, and Microsoft's AI strategies"
Agent: *spawns 3 scout workers simultaneously*
  - scout:sub:001 → Apple
  - scout:sub:002 → Google  
  - scout:sub:003 → Microsoft
*all report back within 60 seconds*
*agent synthesizes and delivers*
Time: 1 minute
```

## Self-Check Questions

Before starting multi-item work, ask:

1. **Are items independent?** → If yes, parallelize
2. **Would I repeat similar steps for each?** → If yes, parallelize
3. **Does order matter?** → If no, parallelize
4. **Is this >3 items?** → If yes, strongly consider parallelizing

## Anti-Patterns

❌ Spawning for single items (overhead not worth it)
❌ Spawning when items depend on each other
❌ Spawning 20+ workers simultaneously (rate limits)
❌ Forgetting to aggregate results after spawn

## Integration

Add to your AGENTS.md:

```markdown
### Sub-Agent Parallelization

When receiving tasks with multiple items (research 5 leads, create 3 drafts, etc.):
1. Check if items are independent
2. Spawn sub-agents for parallel execution
3. Aggregate results when all complete
4. Deliver synthesized output

Use `sessions_spawn` with appropriate agentId. Batch large requests (5-8 at a time).
```
