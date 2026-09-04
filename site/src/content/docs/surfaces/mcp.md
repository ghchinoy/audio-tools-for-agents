---
title: Model Context Protocol (MCP)
description: Stdio JSON-RPC server configuration and available agent tools.
---

`audio-tools-for-agents` includes a native Model Context Protocol (MCP) server powered by FastMCP. It allows AI agents to inspect audio files and extract stems directly without managing shell subprocesses or parsing stdout streams.

## Registration Configuration

Add the following to your agent configuration file (for Claude Desktop, OpenCode, or Cursor):

```json
{
  "mcpServers": {
    "audio-tools": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/absolute/path/to/audio-tools-for-agents",
        "python",
        "-m",
        "audio_tools.mcp_server"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

When used inside an Agent Plugin package, the `${PLUGIN_ROOT}` token is automatically expanded per Agent Plugins Specification §9.2:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "audio-tools": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "${PLUGIN_ROOT}",
        "python",
        "-m",
        "audio_tools.mcp_server"
      ]
    }
  }
}
```

## Available MCP Tools

### 1. `separate_stems`

Separates a mixed audio track into discrete vocal and instrumental stems using HTDemucs.

* **Parameters:**
  * `input_path` (string, required): Local file path or cloud URI (`gs://`).
  * `output_dir` (string, optional, default: `"output"`): Output destination directory or cloud prefix.
  * `stems_count` (integer, optional, default: `4`): Number of stems (`4` or `6`).
  * `device` (string, optional, default: `"cpu"`): Device selection (`"cpu"` or `"auto"`).
* **Returns:** JSON object containing output stem file paths, 100-point normalized waveform peaks, and telemetry metrics.

### 2. `inspect_audio`

Inspects audio metadata for an input file.

* **Parameters:**
  * `file_path` (string, required): Local path or cloud URI.
* **Returns:** JSON object containing `duration_sec`, `samplerate`, `channels`, `format`, and `file_size_mb`.

### 3. `benchmark_system`

Evaluates host hardware to qualify available resources for audio inference.

* **Parameters:** None.
* **Returns:** JSON object with CPU cores, total RAM, available RAM, detected hardware acceleration, and model qualification status.
