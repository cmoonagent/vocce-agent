"use strict";
// n8n community node: transcribe an audio/video file (from a binary property) via vocce's
// hosted Whisper backend. No API key. Multipart is built manually for portability across
// n8n http-helper versions; polling tolerates transient tunnel blips.
const { NodeOperationError } = require("n8n-workflow");

const UA = "vocce-n8n/1.0";

class Vocce {
  constructor() {
    this.description = {
      displayName: "vocce",
      name: "vocce",
      icon: "file:vocce.svg",
      group: ["transform"],
      version: 1,
      subtitle: '={{"transcribe: " + $parameter["binaryPropertyName"]}}',
      description: "Transcribe audio/video to text + SRT/VTT via vocce hosted Whisper (no API key)",
      defaults: { name: "vocce" },
      inputs: ["main"],
      outputs: ["main"],
      properties: [
        {
          displayName: "Binary Property",
          name: "binaryPropertyName",
          type: "string",
          default: "data",
          required: true,
          description: "Name of the binary property holding the audio/video file",
        },
        {
          displayName: "Language",
          name: "language",
          type: "string",
          default: "",
          placeholder: "auto",
          description: "ISO code like 'en', 'zh'. Leave empty to auto-detect.",
        },
        {
          displayName: "API Base URL",
          name: "apiBase",
          type: "string",
          default: "https://api.vocce.io/api/v1",
          description: "Override the vocce backend endpoint",
        },
      ],
    };
  }

  async execute() {
    const items = this.getInputData();
    const out = [];

    for (let i = 0; i < items.length; i++) {
      const binProp = this.getNodeParameter("binaryPropertyName", i);
      const language = this.getNodeParameter("language", i);
      const apiBase = String(this.getNodeParameter("apiBase", i)).replace(/\/$/, "");

      this.helpers.assertBinaryData(i, binProp);
      const buffer = await this.helpers.getBinaryDataBuffer(i, binProp);
      const meta = items[i].binary[binProp];
      const filename = (meta && meta.fileName) || "audio";

      // build multipart/form-data body manually
      const boundary = "----vocce" + Date.now().toString(16) + i;
      const parts = [];
      if (language) {
        parts.push(Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="language"\r\n\r\n${language}\r\n`));
      }
      parts.push(Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${filename}"\r\nContent-Type: ${(meta && meta.mimeType) || "application/octet-stream"}\r\n\r\n`));
      parts.push(buffer);
      parts.push(Buffer.from(`\r\n--${boundary}--\r\n`));
      const body = Buffer.concat(parts);

      const created = await this.helpers.httpRequest({
        method: "POST",
        url: `${apiBase}/transcribe`,
        body,
        headers: { "Content-Type": `multipart/form-data; boundary=${boundary}`, "User-Agent": UA },
        json: true,
      });
      const taskId = (typeof created === "string" ? JSON.parse(created) : created).task_id;
      if (!taskId) throw new NodeOperationError(this.getNode(), "backend did not return a task_id", { itemIndex: i });

      let result = null;
      for (let k = 0; k < 160; k++) {
        await new Promise((r) => setTimeout(r, 2500));
        let s;
        try {
          s = await this.helpers.httpRequest({
            method: "GET",
            url: `${apiBase}/transcribe/tasks/${taskId}`,
            headers: { "User-Agent": UA },
            json: true,
          });
        } catch (e) {
          continue; // transient tunnel blip — retry next tick
        }
        s = typeof s === "string" ? JSON.parse(s) : s;
        if (s.status === "done" || s.status === "completed") { result = s.result || {}; break; }
        if (s.status === "failed") throw new NodeOperationError(this.getNode(), s.error || "transcription failed", { itemIndex: i });
      }
      if (result === null) throw new NodeOperationError(this.getNode(), "timed out waiting for transcription", { itemIndex: i });

      out.push({ json: result, pairedItem: { item: i } });
    }

    return [out];
  }
}

module.exports = { Vocce };
