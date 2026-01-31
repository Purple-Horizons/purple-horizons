# 🦞 OpenClaw Resources

Purple Horizons' collection of skills, tools, and resources for [OpenClaw](https://github.com/openclaw/openclaw) — the open-source AI agent platform.

## Skills

| Skill | Description |
|-------|-------------|
| [session-continuity](./skills/session-continuity/) | Never lose context to compaction. Proactive state management for uninterrupted agent work. |
| [subagent-optimizer](./skills/subagent-optimizer/) | Identify opportunities to parallelize work using sub-agents. Turn sequential tasks into concurrent execution. |

## Related Projects

| Project | Description |
|---------|-------------|
| [openclaw-porter](https://github.com/Purple-Horizons/openclaw-porter) | Export and import OpenClaw agents with full context |
| [openclaw-voice](https://github.com/Purple-Horizons/openclaw-voice) | Self-hosted browser-based voice interface for AI assistants |

## Installation

### Manual

1. Clone this repo
2. Copy the skill folder to your OpenClaw skills directory:
   ```bash
   cp -r openclaw/skills/session-continuity ~/.openclaw/skills/
   ```
3. Restart your agent

## About OpenClaw

OpenClaw is an open-source agentic AI assistant that lives in your terminal, messaging apps, and anywhere you need it. Built for power users who want full control over their AI workflows.

- **GitHub:** [openclaw/openclaw](https://github.com/openclaw/openclaw)
- **Docs:** [docs.openclaw.ai](https://docs.openclaw.ai)
- **Discord:** [discord.gg/clawd](https://discord.gg/clawd)

## Contributing

We welcome contributions! If you've built a useful skill or tool for OpenClaw:

1. Fork this repo
2. Add your skill to `openclaw/skills/`
3. Submit a PR with a README explaining the skill

## License

MIT
