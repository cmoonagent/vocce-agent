#!/usr/bin/env python3
"""vocce transcription CLI — upload a local audio/video file, get text/SRT/VTT.

Talks to vocce's hosted Whisper backend (no API key needed). Pure stdlib.

  python3 transcribe.py meeting.mp3                  # -> plain text
  python3 transcribe.py talk.mp4 --language en --format srt
  VOCCE_API_BASE=https://api.vocce.io/api/v1 python3 transcribe.py a.wav   (default base shown)
"""
import argparse, json, mimetypes, os, pathlib, time, uuid, urllib.request, urllib.error

API = (os.environ.get("VOCCE_API_BASE") or "https://api.vocce.io/api/v1").rstrip("/")
# Cloudflare blocks the default "Python-urllib/x.y" UA (403 / error 1010); any UA passes.
UA = "vocce-cli/1.0"


def _multipart(fields, file_path):
    boundary = "----vocce" + uuid.uuid4().hex
    out = b""
    for k, v in fields.items():
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    fp = pathlib.Path(file_path).expanduser()
    if not fp.exists():
        raise SystemExit(f"file not found: {fp}")
    mime = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
    out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fp.name}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n").encode()
    out += fp.read_bytes() + b"\r\n" + f"--{boundary}--\r\n".encode()
    return boundary, out


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def transcribe(path, language):
    fields = {}
    if language and language != "auto":
        fields["language"] = language
    boundary, body = _multipart(fields, path)
    req = urllib.request.Request(
        f"{API}/transcribe", data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            created = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"create failed: HTTP {e.code} {e.read().decode(errors='replace')[:200]}")
    tid = created.get("task_id")
    if not tid:
        raise SystemExit(f"create failed: {created}")
    for _ in range(160):
        time.sleep(2.5)
        s = _get(f"{API}/transcribe/tasks/{tid}")
        if s.get("status") in ("completed", "done"):
            return s.get("result") or {}
        if s.get("status") == "failed":
            raise SystemExit(f"transcription failed: {s.get('error')}")
    raise SystemExit("timed out waiting for transcription")


def main():
    ap = argparse.ArgumentParser(description="vocce transcription CLI")
    ap.add_argument("file", help="local audio/video file path")
    ap.add_argument("--language", default="auto", help="en / zh / ja / … or auto (default)")
    ap.add_argument("--format", choices=["text", "srt", "vtt", "json"], default="text")
    a = ap.parse_args()
    r = transcribe(a.file, a.language)
    if a.format == "json":
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(r.get(a.format if a.format != "text" else "text", ""))


if __name__ == "__main__":
    main()
