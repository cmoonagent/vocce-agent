# vocce transcription Skill — distribution kit

Paste-ready metadata for listing the vocce transcription **Agent Skill**. Nothing here publishes
automatically.

## Canonical metadata

| Field | Value |
|---|---|
| Skill name | `vocce-transcription` |
| Display name | vocce transcription |
| Category | transcription (speech-to-text) |
| Description | Transcribe audio/video files into text + subtitles (SRT/VTT) via vocce's hosted Whisper. No API key. |
| Repo | https://github.com/cmoonagent/vocce-agent |
| Skill path | `agent-transcription-skill/` (`SKILL.md` + `scripts/transcribe_agent.py`) |
| Homepage | https://vocce.io |
| Requirements | Python 3 (stdlib only — no `pip install`) |
| License | MIT |

## How users install it (manual — always works)

Copy the `agent-transcription-skill/` folder into the agent's skills directory, e.g. for Claude Code:
```bash
# project-scoped
mkdir -p .claude/skills && cp -r agent-transcription-skill .claude/skills/vocce-transcription
# or personal
cp -r agent-transcription-skill ~/.claude/skills/vocce-transcription
```
The skill auto-loads via its `SKILL.md` frontmatter (`name` + `description`).

## As a Claude Code plugin (one-command install)

To make the repo installable with `/plugin marketplace add cmoonagent/vocce-agent`, add these
manifests (verify field names against the current Claude Code plugin docs before relying on them):

`.claude-plugin/marketplace.json`
```json
{
  "name": "vocce",
  "owner": { "name": "vocce", "url": "https://vocce.io" },
  "plugins": [
    {
      "name": "vocce-transcription",
      "source": "./agent-transcription-skill",
      "description": "Transcribe audio/video to text + subtitles via vocce hosted Whisper. No API key."
    }
  ]
}
```

## Community submissions

### awesome-agent-skills / awesome-claude-skills — open a PR
Add one line under the closest category (transcription / media / productivity):
```
- [vocce-transcription](https://github.com/cmoonagent/vocce-agent/tree/main/agent-transcription-skill) - Transcribe audio/video to text + SRT/VTT via hosted Whisper large-v3. No API key, stdlib-only.
```

### Other Skill marketplaces
Use the canonical metadata above. Most expect: name, description, category, repo/source URL, and an
install/usage snippet (the manual copy step above).

## Links
- API docs — https://vocce.io/api
- Source — https://github.com/cmoonagent/vocce-agent
