---
name: vocce-transcription
description: Transcribe audio or video files into text and subtitles (SRT/VTT) using vocce's hosted Whisper. Use when the user gives a local media file and wants a transcript, captions, or subtitles.
---

# vocce transcription skill

Turn any local audio/video file into clean text + SRT + VTT via vocce's hosted
Whisper large-v3 backend. No API key required.

## When to use
- The user provides an audio/video file (mp3, wav, m4a, mp4, mov, …) and wants a
  transcript, captions, or subtitles.
- Files up to 50 MB. Language auto-detected, or pass an ISO code (`en`, `zh`, …).

## How to use
Run the bundled script:

```bash
python3 scripts/transcribe_agent.py /path/to/file.mp4 --language auto --format text
# --format: text (default) | srt | vtt | json
```

Or import it:

```python
from scripts.transcribe_agent import transcribe
result = transcribe("/path/to/file.mp3", language="en")
# result = {"text": "...", "srt": "...", "vtt": "...", "language": "en"}
```

## Notes
- Endpoint defaults to `https://api.vocce.io/api/v1`; override with the
  `VOCCE_API_BASE` env var if self-hosting.
- The call blocks until transcription finishes (polls every ~2.5s).
- Only stdlib is used — no `pip install` needed.
