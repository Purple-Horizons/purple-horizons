# Sub-Agent Optimizer

Teaches AI agents to recognize opportunities for parallel sub-agent execution.

## The Problem

Agents default to sequential processing. When asked to "research 5 companies," they research one, then the next, then the next. This wastes time when items are independent.

## The Solution

Pattern recognition for parallelizable work. Agents learn to:
- Identify multi-item independent tasks
- Spawn sub-agents for parallel execution
- Aggregate results efficiently

## Triggers

- "Research these N items"
- "Create N variations"
- "Check all of these"
- "For each X, do Y"
- Any batch operation with 3+ independent items

## Example

**Before:** 5 lead research tasks → 5 minutes sequential
**After:** 5 scout workers in parallel → 1 minute

## Installation

```bash
# Already in your skills directory
# Skill auto-loads when patterns match
```

## Integration

Add to agent's AGENTS.md for persistent behavior:

```markdown
### Sub-Agent Parallelization
When receiving multi-item tasks, spawn sub-agents for parallel execution.
See skill: subagent-optimizer
```

## License

MIT
