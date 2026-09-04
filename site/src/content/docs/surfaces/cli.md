---
title: Agent-Aware CLI
description: Dual-mode command-line interface design for human developers and autonomous agents.
---

The `audio-tools` command-line tool implements the Dual-Experience (DX and AX) paradigm. It balances rich visual terminal output for human operators with deterministic, single-object JSON for autonomous coding agents.

## Global Tool Installation

To use `audio-tools` directly anywhere on your system without prefixing commands with `uv run`:

```bash
uv tool install git+https://github.com/ghchinoy/audio-tools-for-agents.git
```

This places `audio-tools` directly into `~/.local/bin/audio-tools` in an isolated environment.

## Dual-Mode Operation

### Human Developer Mode (DX)

When invoked without `--json`, the CLI provides colorized progress banners, file paths, and telemetry summary tables:

```bash
uv run audio-tools separate track.wav -o ./output --stems 4
```

```text
Starting HTDemucs stem separation...
  Input:   track.wav
  Output:  ./output
  Stems:   4
  Device:  cpu

Separation successfully completed!

Output Stems:
  - drums   : ./output/track_(Drums)_htdemucs.wav
  - bass    : ./output/track_(Bass)_htdemucs.wav
  - other   : ./output/track_(Other)_htdemucs.wav
  - vocals  : ./output/track_(Vocals)_htdemucs.wav

Telemetry:
  - Audio Duration:   184.2s
  - Inference Time:   72.1s
  - Real-Time Factor: 0.391
  - Peak Memory:      2412.3 MB
  - Device / Cores:   cpu (8 threads)
```

### Agent Automation Mode (AX)

When `--json` is supplied, all diagnostic messages, progress indicators, and library logs are routed to `stderr`. Only a single valid JSON object is printed to `stdout`:

```bash
uv run audio-tools separate track.wav -o ./output --stems 4 --json
```

```json
{
  "status": "success",
  "input_path": "track.wav",
  "output_dir": "./output",
  "stems_count": 4,
  "model_name": "htdemucs",
  "device": "cpu",
  "stems": {
    "drums": "/path/to/output/track_(Drums)_htdemucs.wav",
    "bass": "/path/to/output/track_(Bass)_htdemucs.wav",
    "other": "/path/to/output/track_(Other)_htdemucs.wav",
    "vocals": "/path/to/output/track_(Vocals)_htdemucs.wav"
  },
  "peaks": {
    "drums": [0.12, 0.45, 0.89],
    "vocals": [0.05, 0.22, 0.61]
  },
  "metrics": {
    "model_name": "htdemucs",
    "stems_count": 4,
    "device": "cpu",
    "cpu_threads": 8,
    "audio_duration_sec": 184.2,
    "inference_time_sec": 72.1,
    "total_time_sec": 74.3,
    "real_time_factor": 0.391,
    "peak_rss_mb": 2412.3,
    "memory_delta_mb": 580.4
  }
}
```

## Exit Codes

* `0`: Operation succeeded.
* `1`: Input error or missing file (`ERR_FILE_NOT_FOUND` or `ERR_INFERENCE_FAILED`).
* `2`: Resource constraint warning (`ERR_LOW_MEMORY` when available RAM is $< 2.5\text{GB}$).
