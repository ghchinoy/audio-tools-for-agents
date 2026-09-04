---
name: audio-stemming
description: Separate mixed audio tracks into isolated vocal and instrumental stems (vocals, drums, bass, guitar, piano, other) using local HTDemucs PyTorch inference. Use when an agent needs to isolate vocals, strip drums or accompaniment, or extract multitrack stems from WAV or MP3 files.
license: Apache-2.0
compatibility: Requires uv, Python >= 3.11, ffmpeg, and >= 3GB available RAM.
metadata:
  author: ghchinoy
  version: "0.1.0"
  tags: ["audio", "stems", "htdemucs", "music-processing", "separation"]
---

# Audio Stem Separation (`audio-stemming`)

Isolate mixed audio recordings into discrete instrumental and vocal tracks using Meta's **HTDemucs** (Hybrid Transformer Demucs) models via `audio-tools`.

## Progressive Disclosure & Reference Guides

- [`references/stemmer-matrix.md`](references/stemmer-matrix.md) — 4-stem vs 6-stem capabilities, memory ceilings, and Real-Time Factor (RTF) curves.
- [`references/error-catalog.md`](references/error-catalog.md) — Machine-actionable remediation codes for OOM, missing dependencies, and input format issues.
- [`assets/sample_meta.json`](assets/sample_meta.json) — Schema for machine-readable JSON output and telemetry.

## Available Modes

### Mode 1: Automated Agent Invocation (Machine-Readable JSON)

Autonomous agents must invoke the CLI with the `--json` flag. This directs all progress and logging to `stderr` and guarantees parseable JSON on `stdout`:

```bash
uv run audio-tools separate /path/to/input.wav -o /path/to/output --stems 4 --json
```

**JSON Output Format:**
```json
{
  "status": "success",
  "input_path": "/path/to/input.wav",
  "output_dir": "/path/to/output",
  "stems_count": 4,
  "model_name": "htdemucs.yaml",
  "device": "cpu",
  "stems": {
    "vocals": "/path/to/output/input_(Vocals)_htdemucs.wav",
    "drums": "/path/to/output/input_(Drums)_htdemucs.wav",
    "bass": "/path/to/output/input_(Bass)_htdemucs.wav",
    "other": "/path/to/output/input_(Other)_htdemucs.wav"
  },
  "metrics": {
    "audio_duration_sec": 120.0,
    "inference_time_sec": 48.2,
    "real_time_factor": 0.402,
    "peak_rss_mb": 2450.12
  }
}
```

### Mode 2: 6-Stem Pro Extraction

When piano and guitar separation is required:

```bash
uv run audio-tools separate /path/to/input.wav -o /path/to/output --stems 6 --json
```

*Note:* 6-stem separation requires $\ge 3.5\text{GB}$ available system memory.

### Mode 3: Hardware Acceleration Selection

* **Default (`--device cpu`):** Strictly pinned multi-threaded CPU inference. Safe and predictable across headless Linux VMs, cloud runners, and local workstations.
* **Auto-Detect (`--device auto`):** Automatically selects Apple Silicon Metal (`mps`) or NVIDIA CUDA (`cuda`) if present, falling back to CPU if unavailable:

```bash
uv run audio-tools separate /path/to/input.wav -o /path/to/output --device auto --json
```

### Mode 4: Audio Pre-Flight Inspection

Before executing heavy separation, inspect the source file to verify duration and format:

```bash
uv run audio-tools inspect /path/to/input.wav --json
```

## Agent Safety & Execution Checklist

1. **Verify Available Memory:** Run `uv run audio-tools benchmark --json` before heavy batch jobs. If available RAM is below 2.5GB, warn the user before proceeding.
2. **Never Stream Raw Audio over Context:** Always pass file paths and read JSON metadata. Do not attempt to base64-encode full audio tracks into agent context windows.
3. **Handle Errors Proactively:** Inspect `error_code` on failure (`ERR_LOW_MEMORY`, `ERR_FILE_NOT_FOUND`). See [`references/error-catalog.md`](references/error-catalog.md).
