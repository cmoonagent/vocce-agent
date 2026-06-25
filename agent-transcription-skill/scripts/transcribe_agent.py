#!/usr/bin/env python3
"""vocce transcription helper for agents — importable and runnable.

    from transcribe_agent import transcribe
    r = transcribe("/path/audio.mp3", language="en")   # -> {"text","srt","vtt","language"}

Or from the shell:
    python3 transcribe_agent.py /path/audio.mp4 --language auto --format text

Talks to vocce's hosted Whisper backend (no API key). Pure stdlib.
Override the endpoint with VOCCE_API_BASE (default https://api.vocce.io/api/v1).
"""
import argparse, json, mimetypes, os, pathlib, time, uuid, urllib.request, urllib.error

API = (os.environ.get("VOCCE_API_BASE") or "https://api.vocce.io/api/v1").rstrip("/")
# Cloudflare blocks the default "Python-urllib/x.y" UA (403 / error 1010); any UA passes.
UA = "vocce-skill/1.0"


def _multipart(fields, file_path):
    boundary = "----vocce" + uuid.uuid4().hex
    out = b""
    for k, v in fields.items():
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    fp = pathlib.Path(file_path).expanduser()
    if not fp.exists():
        raise FileNotFoundError(fp)
    mime = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
    out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fp.name}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n").encode()
    out += fp.read_bytes() + b"\r\n" + f"--{boundary}--\r\n".encode()
    return boundary, out


def transcribe(path, language="auto"):
    """Upload a local audio/video file, wait for transcription, return its result dict."""
    fields = {} if (not language or language == "auto") else {"language": language}
    boundary, body = _multipart(fields, path)
    req = urllib.request.Request(
        f"{API}/transcribe", data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        tid = json.loads(r.read().decode()).get("task_id")
    if not tid:
        raise RuntimeError("backend did not return a task_id")
    for _ in range(160):
        time.sleep(2.5)
        poll = urllib.request.Request(f"{API}/transcribe/tasks/{tid}", headers={"User-Agent": UA})
        with urllib.request.urlopen(poll, timeout=30) as r:
            s = json.loads(r.read().decode())
        if s.get("status") in ("completed", "done"):
            return s.get("result") or {}
        if s.get("status") == "failed":
            raise RuntimeError(f"transcription failed: {s.get('error')}")
    raise TimeoutError("timed out waiting for transcription")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="vocce transcription helper")
    ap.add_argument("file")
    ap.add_argument("--language", default="auto")
    ap.add_argument("--format", choices=["text", "srt", "vtt", "json"], default="text")
    a = ap.parse_args()
    res = transcribe(a.file, a.language)
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.format == "json"
          else res.get(a.format if a.format != "text" else "text", ""))
