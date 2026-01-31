---
name: subagent-optimizer
description: Identify opportunities to parallelize work using sub-agents. Use when receiving multi-item tasks, batch operations, or work that could benefit from concurrent execution. Triggers on phrases like "research these 5 companies", "create 3 variations", "check all of these", or any task with multiple independent items.
---

# Sub-Agent Optimizer

Recognize when to spawn sub-agents for parallel execution, and audit agent configs to enable sub-agent capabilities.

## Two Modes

### 1. Runtime Mode (Pattern Recognition)
Triggers automatically when receiving parallelizable tasks.

### 2. Audit Mode (Config Optimization)
Triggers on: "optimize agents", "audit agent config", "check subagent permissions"

## Runtime Mode: Decision Framework

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
| "Research these N items" | "Research these 5 companies" | Spawn N research workers |
| "Create N variations" | "Write 3 headline options" | Spawn N content workers |
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
        agentId="research-agent",  # or same type for parallel work
        task=f"[Specific task for {item}]. Return: [expected output format]."
    )

# Results announce back → aggregate → deliver
```

## Sub-Agent Selection

| Task Type | Spawn Agent Type | Why |
|-----------|------------------|-----|
| Research, fact-finding | Research-specialized agent | Optimized for discovery |
| Content drafts, copy | Content agent (or self) | Voice-consistent |
| Data processing | Self (parallel instances) | Same capabilities needed |
| Personalization at scale | Self | Context-aware |

## Audit Mode: Config Optimization

When triggered with "optimize agents" or "audit agent config":

### Step 1: Read Current Config

```bash
cat ~/.openclaw/openclaw.json | jq '.agents.list[] | {id: .id, name: .name, subagents: .subagents}'
```

### Step 2: Analyze Each Agent

For each agent, check:
- Can it spawn sub-agents of its own type? (parallel self-work)
- Can it spawn research agents? (delegation)
- Can it escalate to orchestrator? (getting help)

### Step 3: Identify Gaps

Common issues:
- Agent can only spawn "main" (can't parallelize own work)
- Research agent can't spawn itself (can't parallel research)
- Content agent can't spawn research (can't delegate discovery)

### Step 4: Recommend Fixes

```
AUDIT RESULTS:

✅ orchestrator: Can spawn [content, research, sales] — Good
⚠️  content-agent: Can only spawn [main] — Limited
   → Recommend: Add [content, research] for parallel drafts + research delegation
⚠️  research-agent: Can only spawn [main] — Limited  
   → Recommend: Add [research] for parallel deep-dives
✅ sales-agent: Can spawn [sales, research, main] — Good

Apply recommended fixes? [y/n]
```

### Step 5: Apply Fixes (with confirmation)

Edit `~/.openclaw/openclaw.json` to update `subagents.allowAgents` arrays, then:

```bash
# Restart gateway to apply
openclaw gateway restart --reason "Updated subagent permissions"
```

## Example Audit Script

```python
# Pseudo-code for audit logic
def audit_agents():
    config = read_config("~/.openclaw/openclaw.json")
    recommendations = []
    
    for agent in config.agents.list:
        allowed = agent.subagents.allowAgents or []
        agent_type = agent.id
        
        # Check: Can agent parallelize its own work?
        if agent_type not in allowed:
            recommendations.append({
                "agent": agent_type,
                "add": agent_type,
                "reason": "Enable parallel self-spawning"
            })
        
        # Check: Can agent delegate research?
        if "research" not in allowed and agent_type != "research":
            recommendations.append({
                "agent": agent_type,
                "add": "research",
                "reason": "Enable research delegation"
            })
    
    return recommendations
```

## Integration

Add to AGENTS.md for persistent behavior:

```markdown
### Sub-Agent Parallelization

When receiving tasks with multiple items:
1. Check if items are independent
2. Spawn sub-agents for parallel execution
3. Aggregate results when all complete

Use `sessions_spawn` with appropriate agentId. Batch large requests (5-8 at a time).

To audit permissions: "optimize agents" or "audit agent config"
```

## Anti-Patterns

❌ Spawning for single items (overhead not worth it)
❌ Spawning when items depend on each other
❌ Spawning 20+ workers simultaneously (rate limits)
❌ Forgetting to aggregate results after spawn
❌ Agents that can't spawn themselves (limits parallelization)
