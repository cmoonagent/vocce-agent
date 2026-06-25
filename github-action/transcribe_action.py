#!/usr/bin/env python3
"""GitHub Action entrypoint — transcribe a file via vocce's hosted backend.

Reads inputs from env (set by action.yml), writes outputs to $GITHUB_OUTPUT.
Pure stdlib. No API key needed.
"""
import json, mimetypes, os, pathlib, sys, time, uuid, urllib.request, urllib.error

API = (os.environ.get("VOCCE_API_BASE") or "https://api.vocce.io/api/v1").rstrip("/")
UA = "vocce-gha/1.0"  # the default Python-urllib UA is blocked by Cloudflare; any UA passes


def _open(req, timeout, tries=5):
    """urlopen with retry on transient network/TLS errors and 5xx (the tunnel can blip)."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode()
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt < tries - 1:
                time.sleep(3); continue
            raise
        except urllib.error.URLError:  # includes SSL EOF, timeouts, conn reset
            if attempt < tries - 1:
                time.sleep(3); continue
            raise


def _multipart(fields, fp):
    boundary = "----vocce" + uuid.uuid4().hex
    out = b""
    for k, v in fields.items():
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    mime = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
    out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fp.name}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n").encode()
    out += fp.read_bytes() + b"\r\n" + f"--{boundary}--\r\n".encode()
    return boundary, out


def main():
    file_in = os.environ.get("VOCCE_FILE", "").strip()
    language = os.environ.get("VOCCE_LANGUAGE", "auto").strip()
    fmt = (os.environ.get("VOCCE_FORMAT", "text").strip() or "text")
    fp = pathlib.Path(file_in).expanduser()
    if not file_in or not fp.exists():
        print(f"::error::file not found: {file_in}")
        sys.exit(1)

    fields = {} if (not language or language == "auto") else {"language": language}
    boundary, body = _multipart(fields, fp)
    req = urllib.request.Request(
        f"{API}/transcribe", data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": UA},
    )
    try:
        tid = json.loads(_open(req, 180)).get("task_id")
    except urllib.error.HTTPError as e:
        print(f"::error::create failed: HTTP {e.code} {e.read().decode(errors='replace')[:200]}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"::error::create failed: {e}")
        sys.exit(1)
    if not tid:
        print("::error::backend did not return a task_id")
        sys.exit(1)

    result = None
    for _ in range(160):
        time.sleep(2.5)
        poll = urllib.request.Request(f"{API}/transcribe/tasks/{tid}", headers={"User-Agent": UA})
        try:
            s = json.loads(_open(poll, 30))
        except urllib.error.URLError:
            continue  # transient blip — try again next tick
        if s.get("status") in ("done", "completed"):
            result = s.get("result") or {}
            break
        if s.get("status") == "failed":
            print(f"::error::transcription failed: {s.get('error')}")
            sys.exit(1)
    if result is None:
        print("::error::timed out waiting for transcription")
        sys.exit(1)

    out_text = json.dumps(result, ensure_ascii=False, indent=2) if fmt == "json" \
        else result.get(fmt if fmt != "text" else "text", "")

    # write a result file in the workspace
    ext = "json" if fmt == "json" else fmt
    result_file = f"vocce-transcript.{ext}"
    pathlib.Path(result_file).write_text(out_text, encoding="utf-8")

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"result<<VOCCE_EOF\n{out_text}\nVOCCE_EOF\n")
            f.write(f"result_file={result_file}\n")
    print(f"vocce: transcribed {fp.name} -> {result_file} ({len(out_text)} chars)")


if __name__ == "__main__":
    main()
