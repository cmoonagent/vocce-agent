# n8n-nodes-vocce

An [n8n](https://n8n.io) community node that transcribes an audio/video file to text + SRT/VTT via
vocce's hosted Whisper large-v3. **No API key.**

## Install

n8n → **Settings → Community Nodes → Install** → `n8n-nodes-vocce`
(or `npm i n8n-nodes-vocce` in a self-hosted instance).

## Node: vocce

Feed it an item with a **binary property** containing the media file (e.g. from a *Read Binary File*
or *HTTP Request* node).

| Parameter | Default | Description |
|---|---|---|
| Binary Property | `data` | Name of the binary property holding the file |
| Language | _(empty = auto)_ | ISO code like `en`, `zh` |
| API Base URL | `https://api.vocce.io/api/v1` | Override endpoint |

**Output** (`json`): `{ text, srt, vtt, language, duration, segments }`.

## Notes

- The node uploads the file, polls until done, and tolerates transient backend blips.
- Files up to 50 MB.

> ⚠️ Before publishing to npm / the n8n community registry, smoke-test in a live n8n instance —
> n8n's binary/http helpers vary slightly across versions. Built against the n8n-workflow v1 node API.

## License
MIT
