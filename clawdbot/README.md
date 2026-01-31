# 🦞 Clawdbot Resources

Purple Horizons' collection of skills, tools, and resources for [Clawdbot](https://github.com/clawdbot/clawdbot) — the open-source AI agent platform.

## Skills

| Skill | Description |
|-------|-------------|
| [session-continuity](./skills/session-continuity/) | Never lose context to compaction. Proactive state management for uninterrupted agent work. |
| [subagent-optimizer](./skills/subagent-optimizer/) | Identify opportunities to parallelize work using sub-agents. Turn sequential tasks into concurrent execution. |
| [x-engagement](./skills/x-engagement/) | Auto-find and reply to people with relevant pain points when you post on X. Two rounds max (8 replies) to stay safe from throttling. |

## Related Projects

| Project | Description |
|---------|-------------|
| [openclaw-porter](https://github.com/Purple-Horizons/openclaw-porter) | Export and import Clawdbot agents with full context |
| [openclaw-voice](https://github.com/Purple-Horizons/openclaw-voice) | Self-hosted browser-based voice interface for AI assistants |

## Installation

### Via ClawdHub (Recommended)

```bash
clawdhub install purple-horizons/session-continuity
```

### Manual

1. Clone this repo
2. Copy the skill folder to your Clawdbot skills directory:
   ```bash
   cp -r clawdbot/skills/session-continuity ~/.clawdbot/skills/
   ```
3. Restart your agent

## About Clawdbot

Clawdbot is an open-source agentic AI assistant that lives in your terminal, messaging apps, and anywhere you need it. Built for power users who want full control over their AI workflows.

- **GitHub:** [clawdbot/clawdbot](https://github.com/clawdbot/clawdbot)
- **Docs:** [docs.clawd.bot](https://docs.clawd.bot)
- **Discord:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Skills:** [clawdhub.com](https://clawdhub.com)

## Contributing

We welcome contributions! If you've built a useful skill or tool for Clawdbot:

1. Fork this repo
2. Add your skill to `clawdbot/skills/`
3. Submit a PR with a README explaining the skill

## License

MIT
