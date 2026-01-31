# X Engagement

An OpenClaw skill that automatically finds people discussing relevant pain points when you post on X/Twitter, then crafts contextual replies to boost visibility.

## Installation

Copy to skills directory:

```bash
cp -r x-engagement ~/.openclaw/skills/
```

## Usage

After posting on X, trigger the skill:

```
Engage on my last X post about [topic]
```

The agent will:
1. Analyze your post's topic and pain point
2. Search for people discussing that problem
3. Show you targets for approval
4. Post contextual replies (not spam)
5. Log everything

## How It Works

### 1. Target Discovery
Searches for:
- People complaining about the problem you solved
- Users asking questions about the topic
- New users of relevant tools who need tips
- Power users who would appreciate the solution

### 2. Smart Filtering
Skips:
- Bot accounts
- Old posts (>48h)
- Posts with 50+ replies (won't be seen)
- Promotional/spam accounts

### 3. Contextual Replies
Each reply:
- References something specific in their post
- Offers genuine value
- Links back naturally
- Sounds human, not templated

### 4. Rate Limiting
Built-in safety:
- 8 replies max per day
- 2 rounds × 4 replies
- 3-5 sec gap between replies
- 30+ min between rounds

## Example

**Your post:**
> "Your AI agent mid-task: 'What was I doing again?' We fixed this. session-continuity writes state BEFORE context fills."

**Targets found:**
- @user1 complaining about manual context management
- @user2 wanting to build a memory agent  
- @user3 just installed OpenClaw
- @user4 writing an OpenClaw tutorial

**Replies posted:**
- "The context struggle is real. This saves state BEFORE it fills — game changer. [link]"
- "Already built exactly this. [link]"
- "Pro tip for new users: grab this early. Trust me. [link]"
- "Great guide! One skill to add for state persistence. [link]"

## Requirements

- `bird` CLI installed and authenticated ([bird docs](https://github.com/steipete/bird))
- Chrome logged into X (bird uses cookie auth)

## Safety Notes

- Quality > quantity. 4 great replies beat 10 generic ones.
- Read their post carefully. Reference something specific.
- If rate limited, stop immediately and wait 24h.
- Don't reply to the same person twice.

## Files

- `SKILL.md` - Full instructions for the agent
- `scripts/engage.sh` - Helper script for searching targets
- Logs to `memory/x-engagement-log.md`

## License

MIT

## Credits

Built by [Purple Horizons](https://purplehorizons.io) for the OpenClaw community.
