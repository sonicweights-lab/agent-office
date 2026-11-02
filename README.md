# The AI Agent Office 🏢

Four Claude Code agents that research, script, animate and review short-form videos: the same office from the [@sonicweights](https://www.instagram.com/sonicweights/) Reel.

| Desk | Agent | What it does |
|---|---|---|
| 🔎 Research | [`research`](.claude/agents/research.md) | Finds what's actually trending, with dated evidence, and picks the angle |
| ✍️ Script | [`script`](.claude/agents/script.md) | Writes a retention-first script: a hook in 2s, a new open loop every few seconds, a payoff, a CTA |
| 🎬 Animate | [`animate`](.claude/agents/animate.md) | Builds the video as code in Remotion (2D, 3D, UI mockups) and times it to the voiceover |
| ✅ Edit | [`edit`](.claude/agents/edit.md) | Reviews the render against a strict checklist; approves it or sends it back |

## Set up (5 minutes)
1. Install [Claude Code](https://claude.com/claude-code).
2. Copy the `.claude/agents/` folder into your project (or into `~/.claude/agents/` to use it everywhere).
3. For voiceovers: `pip install edge-tts`, plus [ffmpeg](https://ffmpeg.org/) on your PATH. `tools/tts.py` turns a script into timed, silence-trimmed voice lines.
4. For video: let the `animate` agent set up Remotion in a `studio/` folder (it asks before installing).

## Run the office
Open Claude Code in your project and say:

> Use the research agent to find a trending angle on **[your topic]**. Then have the script agent write a 20-second Reel from it, the animate agent build and render it, and the edit agent review it. Loop animate → edit until edit approves.

Each agent writes its output into `briefs/<slug>/`, so you can read, change or re-run any step.

## Tips
- Edit is supposed to be harsh. Our first draft got rejected for being flat and hard on the eyes, and the video got much better for it.
- Keep one visual look per channel. Consistency is what makes people recognise you in the feed.
- Facts in a video must come from Research's sources. No source, no claim.

Made by [@sonicweights](https://www.instagram.com/sonicweights/). Comment on the Reel if you build your own office; I'd love to see it.
