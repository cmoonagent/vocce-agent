#!/usr/bin/env node
// vocce transcription MCP server — talks to vocce's hosted whisper backend.
// Exposes a `transcribe` tool: give it a local audio/video file, get back
// text + SRT + VTT. No API key required (the public endpoint is open).
//
//   npm install
//   VOCCE_API_BASE=https://api.vocce.io/api/v1 node server.js   (default base shown)
//
// Add to an MCP client (e.g. Claude):
//   { "mcpServers": { "vocce": { "command": "node", "args": ["/path/to/server.js"] } } }

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync } from "node:fs";
import { basename } from "node:path";

const API = (process.env.VOCCE_API_BASE || "https://api.vocce.io/api/v1").replace(/\/$/, "");
// Explicit UA — node/undici passes Cloudflare today, but be defensive against rule changes.
const UA = "vocce-mcp/1.0";

async function transcribe(filePath, language) {
  const fd = new FormData();
  fd.append("file", new Blob([readFileSync(filePath)]), basename(filePath));
  if (language && language !== "auto") fd.append("language", language);

  const res = await fetch(`${API}/transcribe`, { method: "POST", body: fd, headers: { "User-Agent": UA } });
  const created = await res.json().catch(() => ({}));
  if (!res.ok || !created.task_id) {
    throw new Error(created.detail || `create failed: HTTP ${res.status}`);
  }

  for (let i = 0; i < 160; i++) {
    await new Promise((r) => setTimeout(r, 2500));
    const s = await (await fetch(`${API}/transcribe/tasks/${created.task_id}`, { headers: { "User-Agent": UA } })).json();
    if (s.status === "completed" || s.status === "done") return s.result || {};
    if (s.status === "failed") throw new Error(s.error || "transcription failed");
  }
  throw new Error("timed out waiting for transcription");
}

const server = new McpServer({ name: "vocce-transcribe", version: "1.0.0" });

server.tool(
  "transcribe",
  "Transcribe a local audio or video file to text and subtitles using vocce's hosted Whisper large-v3. Returns plain text, SRT, and VTT.",
  {
    file_path: z.string().describe("Absolute path to a local audio/video file (mp3, wav, m4a, mp4, mov, …). Up to 50MB."),
    language: z.string().optional().describe("ISO code like 'en', 'zh', 'ja'. Omit or 'auto' to auto-detect."),
  },
  async ({ file_path, language }) => {
    const r = await transcribe(file_path, language);
    const out = { text: r.text || "", srt: r.srt || "", vtt: r.vtt || "", language: r.language || null };
    return { content: [{ type: "text", text: JSON.stringify(out, null, 2) }] };
  }
);

await server.connect(new StdioServerTransport());
