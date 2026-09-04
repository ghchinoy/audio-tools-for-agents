# Audio Tools for Agents

> Deterministic audio manipulation and local deep-learning stem separation for AI agents.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![MCP](https://img.shields.io/badge/MCP-2.1.1-green.svg)](mcp.json)
[![Agent_Plugin](https://img.shields.io/badge/Agent_Plugin-v1.0.0-purple.svg)](plugin.json)

`audio-tools-for-agents` provides local, non-cloud audio processing primitives designed specifically for autonomous agents and the agent economy. Its primary capability is multitrack audio stem separation using Meta's HTDemucs (Hybrid Transformer Demucs) models, packaged across four agent-ready surfaces.

---

## 1-Minute Quickstart

Requirements: `uv` and `ffmpeg`.

### Option A: 1-Command Agent & CLI Installer (Recommended)
Automatically installs the CLI to `~/.local/bin/audio-tools` and registers skills for Antigravity and Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/ghchinoy/audio-tools-for-agents/main/scripts/install.sh | bash
```

### Option B: 1-Line Global Tool Install
Install the CLI directly into your global environment without manual cloning:

```bash
uv tool install git+https://github.com/ghchinoy/audio-tools-for-agents.git
```

### Option C: Local Development Clone
```bash
# 1. Clone & install dependencies
git clone https://github.com/ghchinoy/audio-tools-for-agents.git
cd audio-tools-for-agents
uv sync

# 2. Inspect an audio file (metadata, duration, channels)
uv run audio-tools inspect my_song.wav

# 3. Separate into 4 stems (vocals, drums, bass, other)
uv run audio-tools separate my_song.wav -o ./output --stems 4

# 4. Agent AX mode (machine-readable single JSON on stdout)
uv run audio-tools separate my_song.wav -o ./output --stems 4 --json
```

---

## Delivery Surfaces

This repository delivers audio separation capabilities across four standard interoperability surfaces:

### 1. Agent-Aware CLI (`audio-tools`)
A dual-mode terminal interface serving both human developers (rich progress and tables) and autonomous agents (deterministic, unadorned JSON when `--json` is passed).
* **CPU-Only Default:** Guarantees stability across diverse environments.
* **Optional Hardware Acceleration:** Pass `--device auto` to leverage Apple Silicon Metal (`mps`) or NVIDIA CUDA (`cuda`).
* **Fail-Fast Safety:** Checks host RAM before execution. Emits actionable error codes (`ERR_LOW_MEMORY`, `ERR_FILE_NOT_FOUND`) on failure.

### 2. Model Context Protocol (MCP) Server
A standard stdio JSON-RPC server defined in `mcp.json`. Exposes three tools directly to LLM runtimes:
* `separate_stems`: Isolates vocal and instrument tracks, returning file locations and telemetry.
* `inspect_audio`: Retrieves duration, sample rate, channels, format, and file size.
* `benchmark_system`: Reports host core counts, RAM, and hardware acceleration qualification.

To register with Claude Desktop or OpenCode, add to your MCP client config:

```json
{
  "mcpServers": {
    "audio-tools": {
      "command": "uv",
      "args": ["run", "--project", "/absolute/path/to/audio-tools-for-agents", "python", "-m", "audio_tools.mcp_server"]
    }
  }
}
```

### 3. Agent Skill (`skills/audio-stemming`)
Packaged per the [Agent Skills](https://agentskills.io) specification. Features three-stage progressive disclosure:
* **Discovery:** Concise YAML frontmatter description for minimal context token footprint.
* **Activation:** Decision rubric selecting between 4-stem and 6-stem models based on target instrumentation.
* **Execution:** Bundled executable wrapper script (`scripts/separate.sh`) for non-interactive execution.

### 4. Agent Plugin (`plugin.json`)
Conforms to the [Agent Plugins v1.0.0 Specification](https://github.com/agentplugins/agent-plugins-spec), complete with root manifest, component discovery, and marketplace catalog index (`.claude-plugin/marketplace.json`).

---

## Model Selection Matrix

| Stem Count | Model Config | Extracted Tracks | Target Use Case | Required RAM |
| :--- | :--- | :--- | :--- | :--- |
| **4 Stems** (Standard) | `htdemucs.yaml` | Vocals, Drums, Bass, Other | Vocal removal, sampling, acapella creation | >= 3.0 GB |
| **6 Stems** (Pro) | `htdemucs_6s.yaml` | Vocals, Drums, Bass, Guitar, Piano, Other | Multitrack remixing, acoustic transcription | >= 4.0 GB |

---

## Local Development & Testing

```bash
# Run unit and integration tests
make test

# Run code linter and formatting checks
make lint

# Automatically apply formatting
make format

# Start local MCP server over stdio
make mcp

# Validate Agent Plugins and Agent Skills spec compliance
make validate-spec
```

---

## Complementary Projects

`audio-tools-for-agents` focuses exclusively on local deep-learning inference and signal processing without cloud API dependencies. For cloud-native multimodal media pipelines (Gemini ASR, Lyria generative music scoring, and Gemini TTS voice patching), see its sister project:

* **[gemini-bluestone](../gemini-bluestone)**: Cloud multimodal audio studio built in Go and FFmpeg.

---

## License

Apache-2.0. See [LICENSE](LICENSE) for details.
