# vocce transcribe — MCP server

**Transcribe any local audio or video file to text + subtitles, straight from your AI agent.**
Powered by vocce's hosted Whisper large-v3.

✨ **No API key** · ☁️ **Hosted** (no model, no GPU to run) · 🆓 **Free preview**

## Install

Add this to your MCP client config (Claude Desktop, Cursor, Windsurf, …). There's no install step — `npx` fetches it on first run:

```json
{
  "mcpServers": {
    "vocce": {
      "command": "npx",
      "args": ["-y", "vocce-transcribe-mcp"]
    }
  }
}
```

Restart your client and the `transcribe` tool is ready.

## Tool

### `transcribe`

Transcribe a local audio/video file to text, SRT, and VTT.

| Param | Type | Required | Description |
|---|---|---|---|
| `file_path` | string | ✅ | Absolute path to a local audio/video file (`mp3`, `wav`, `m4a`, `mp4`, `mov`, …), up to 50 MB |
| `language` | string | — | ISO code like `en`, `zh`, `ja`. Omit or use `auto` to auto-detect |

Returns JSON: `{ text, srt, vtt, language }`.

**Example prompt:**

> "Transcribe `~/Downloads/interview.mp4` and pull out the action items."

## Configuration

| Env var | Default | Description |
|---|---|---|
| `VOCCE_API_BASE` | `https://api.vocce.io/api/v1` | Override the backend endpoint (self-hosted / staging) |

## How it works

This server is a thin client: it uploads your file to vocce's hosted backend, polls until the job is done, and hands back the result. Transcription runs on vocce's GPU — you don't download or run a model locally.

## Links

- Website — https://vocce.io
- Source — https://github.com/cmoonagent/vocce-agent
- Issues — https://github.com/cmoonagent/vocce-agent/issues

## License

MIT
