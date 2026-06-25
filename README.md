# vocce — agent integrations

Hosted audio/video transcription for AI agents and automations.
**No API key. No local model.** Upload a file, get back text + SRT + VTT + timestamped segments —
powered by Whisper large-v3 on vocce's GPU.

→ Product: https://vocce.io · API docs: https://vocce.io/api · OpenAPI: https://vocce.io/openapi.json

## Three ways to use it

### 1. MCP server — for Claude, Cursor, Windsurf, …
```json
{ "mcpServers": { "vocce": { "command": "npx", "args": ["-y", "vocce-transcribe-mcp"] } } }
```
Details → [`transcribe-mcp-server/`](./transcribe-mcp-server)

### 2. CLI — Python, stdlib only
```bash
python3 transcribe-cli/transcribe.py meeting.mp3 --format srt
```
Details → [`transcribe-cli/`](./transcribe-cli)

### 3. Agent Skill — drop-in for Claude
See → [`agent-transcription-skill/`](./agent-transcription-skill)

## Also in here
- **GitHub Action** — transcribe in CI → [`github-action/`](./github-action)
- **n8n community node** — `n8n-nodes-vocce` → [`n8n-nodes-vocce/`](./n8n-nodes-vocce)
- **Function calling** (OpenAI / Anthropic) + **ChatGPT Action** → [`integrations/`](./integrations)
- **Directory submission kits** (MCP + Skill) → [`distribution/`](./distribution)
- **MCP registry manifest** → [`server.json`](./server.json)

## How it works
Every package is a thin client: it uploads your file to vocce's hosted backend, polls until the job
is done, and returns the result. The transcription runs on vocce's GPU — nothing to install, no model
to download. The backend is the product; these clients are open source (MIT).

## License
MIT
