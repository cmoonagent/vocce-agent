# vocce MCP — directory submission kit

Paste-ready metadata for listing the vocce transcription MCP server. Fill the form / open the PR;
nothing here publishes automatically.

## Canonical metadata (reuse everywhere)

| Field | Value |
|---|---|
| Display name | **vocce transcribe** |
| Registry name | `io.github.cmoonagent/vocce-agent` |
| npm package | `vocce-transcribe-mcp` |
| Short description (≤120) | Transcribe audio/video to text + SRT/VTT via hosted Whisper. No API key. |
| Repo | https://github.com/cmoonagent/vocce-agent |
| Homepage | https://vocce.io |
| Install | `npx -y vocce-transcribe-mcp` |
| Transport | stdio |
| Auth | none |
| Env | `VOCCE_API_BASE` (optional, defaults to hosted API) |
| Tools | `transcribe(file_path, language?)` → `{ text, srt, vtt, language }` |
| License | MIT |
| Categories | transcription, speech-to-text, audio, video |
| Keywords | mcp, transcription, whisper, subtitles, speech-to-text, srt, vtt, audio, video |
| Logo | https://vocce.io/logo.svg |

**Long description:**
> vocce is hosted media infrastructure for agents. This MCP server exposes a single `transcribe`
> tool that turns a local audio or video file into clean text, SRT, and VTT using Whisper large-v3
> running on vocce's GPU — no API key, no local model, no setup. Point it at a file, get structured
> output back. Free preview.

**Client config:**
```json
{
  "mcpServers": {
    "vocce": { "command": "npx", "args": ["-y", "vocce-transcribe-mcp"] }
  }
}
```

---

## Per-directory steps

### Official MCP Registry — registry.modelcontextprotocol.io
Driven by `server.json` (repo root) + `mcpName` in package.json. See `../PUBLISH.md` for the exact
`mcp-publisher` commands. Most other directories ingest from here, so do this first.

### glama.ai
Auto-indexes public GitHub repos that contain an MCP server — no submission needed once the repo is
public with a good README. Optionally sign in and **claim** the listing to manage it.

### mcp.so
Submit via the "Submit" flow on the site using the canonical metadata above (it also ingests from the
official registry, so a registry publish may auto-populate it).

### smithery.ai
Add a `smithery.yaml` at the repo root, then connect the repo on smithery.ai. Suggested file
(verify against smithery's current schema before relying on it):
```yaml
startCommand:
  type: stdio
  configSchema:
    type: object
    properties:
      voCceApiBase:
        type: string
        title: VOCCE_API_BASE
        description: Override the vocce backend endpoint (optional).
  commandFunction: |-
    (config) => ({
      command: 'npx',
      args: ['-y', 'vocce-transcribe-mcp'],
      env: config.voCceApiBase ? { VOCCE_API_BASE: config.voCceApiBase } : {}
    })
```

### awesome-mcp-servers (punkpeye/awesome-mcp-servers) — open a PR
Add one line under the closest existing category (e.g. a media / speech section). Match the repo's
current emoji legend (📇 = TypeScript/Node, ☁️ = cloud service):
```
- [vocce](https://github.com/cmoonagent/vocce-agent) 📇 ☁️ - Transcribe audio/video to text + SRT/VTT via hosted Whisper large-v3. No API key required.
```
