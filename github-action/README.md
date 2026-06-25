# vocce transcribe — GitHub Action

Transcribe an audio/video file to text + SRT/VTT in a workflow, via vocce's hosted Whisper large-v3.
**No API key.**

## Usage

```yaml
- uses: cmoonagent/vocce-agent/github-action@main
  id: vocce
  with:
    file: ./recordings/episode.mp3
    language: en        # or "auto" (default)
    format: srt         # text | srt | vtt | json (default: text)

- run: echo "${{ steps.vocce.outputs.result }}"
# a file (e.g. vocce-transcript.srt) is also written to the workspace,
# path in: ${{ steps.vocce.outputs.result_file }}
```

### Inputs
| Input | Required | Default | Description |
|---|---|---|---|
| `file` | ✅ | — | Path to the audio/video file in the workspace |
| `language` | — | `auto` | ISO code (`en`, `zh`, …) or `auto` |
| `format` | — | `text` | `text` / `srt` / `vtt` / `json` |
| `api_base` | — | `https://api.vocce.io/api/v1` | Override endpoint |

### Outputs
| Output | Description |
|---|---|
| `result` | The transcript in the chosen format |
| `result_file` | Path to the written result file |

Requires Python 3 on the runner (present on `ubuntu-latest`, `macos-latest`, `windows-latest`).
