# vocce — agent integrations

Wire vocce transcription into your own agent or a ChatGPT Custom GPT.
Backend: `https://api.vocce.io/api/v1` · No API key (free preview) · Full spec: https://vocce.io/openapi.json

> Already using Claude / Cursor / an MCP client? Skip all of this and use the **MCP server**:
> `npx -y vocce-transcribe-mcp` (see `../transcribe-mcp-server`).

---

## 1. Function calling (OpenAI / Anthropic SDKs)

Register the `transcribe_audio` tool with your model, then **you** implement the function — it
uploads the file to vocce and polls for the result. Schemas ready to paste:

- OpenAI: [`openai-function-calling.json`](./openai-function-calling.json)
- Anthropic: [`anthropic-tool-use.json`](./anthropic-tool-use.json)

### Reference implementation (Python, stdlib only)

The tool body is the same logic as the CLI in `../transcribe-cli`:

```python
import json, mimetypes, pathlib, time, uuid, urllib.request

API = "https://api.vocce.io/api/v1"
UA = "vocce-fn/1.0"  # any non-default UA (the default Python-urllib UA is blocked by Cloudflare)

def transcribe_audio(file_path: str, language: str | None = None) -> dict:
    fp = pathlib.Path(file_path).expanduser()
    boundary = "----vocce" + uuid.uuid4().hex
    body = b""
    if language and language != "auto":
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="language"\r\n\r\n{language}\r\n'.encode()
    mime = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
    body += (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{fp.name}"\r\n'
             f"Content-Type: {mime}\r\n\r\n").encode() + fp.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{API}/transcribe", data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": UA})
    tid = json.loads(urllib.request.urlopen(req, timeout=180).read())["task_id"]
    for _ in range(160):
        time.sleep(2.5)
        poll = urllib.request.Request(f"{API}/transcribe/tasks/{tid}", headers={"User-Agent": UA})
        s = json.loads(urllib.request.urlopen(poll, timeout=30).read())
        if s.get("status") in ("done", "completed"):
            return s.get("result") or {}
        if s.get("status") == "failed":
            raise RuntimeError(s.get("error"))
    raise TimeoutError("transcription timed out")
```

Feed the returned `result` (or just `result["text"]`) back to the model as the tool result.

---

## 2. ChatGPT Custom GPT (Action)

Create a GPT → **Configure → Actions → Import from URL** → `https://vocce.io/openapi.json`.
Authentication: **None**.

⚠️ **Known limitation — local files.** ChatGPT Actions send JSON, not `multipart/form-data`
file uploads, so a Custom GPT **cannot upload a local audio file** to `POST /transcribe`. The
`GET /transcribe/tasks/{task_id}` poll works fine. Until vocce adds a URL-source endpoint
(`POST` with `{ "source_url": "…" }` — a planned backend follow-up), use the **MCP server** or
**CLI** for local-file transcription; the Custom GPT Action is best for checking/fetching results
of jobs created elsewhere.

---

## Links
- API docs — https://vocce.io/api
- OpenAPI — https://vocce.io/openapi.json
- Source — https://github.com/cmoonagent/vocce-agent
