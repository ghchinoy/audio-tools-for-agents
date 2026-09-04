---
title: Quickstart
description: Get up and running with audio-tools-for-agents in under two minutes.
---

`audio-tools-for-agents` provides deterministic, local audio processing primitives for autonomous AI coding agents and automated workflows.

## Prerequisites

1. **Python:** `>= 3.11, < 3.14` (CPython 3.13 recommended)
2. **Package Manager:** [`uv`](https://docs.astral.sh/uv/)
3. **FFmpeg:** System binary installed in `PATH` (used by PyTorch audio decoders)
4. **Host RAM:** At least 3.0 GB of available system memory

## Installation Options

### Option A: 1-Command Bootstrap (Recommended for Agents)

Installs the `audio-tools` CLI to `~/.local/bin` and links the `audio-stemming` skill to Antigravity and Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/ghchinoy/audio-tools-for-agents/main/scripts/install.sh | bash
```

### Option B: 1-Line Global Tool Install

Install the standalone binary globally without cloning the source repository:

```bash
uv tool install git+https://github.com/ghchinoy/audio-tools-for-agents.git
```

### Option C: Developer Source Clone

```bash
git clone https://github.com/ghchinoy/audio-tools-for-agents.git
cd audio-tools-for-agents

# Install dependencies into managed virtual environment
uv sync
```

## Basic Usage

### 1. Inspect Audio Metadata

Inspect the duration, sample rate, channels, format, and file size of an audio file:

```bash
uv run audio-tools inspect my_song.wav
```

To emit machine-readable JSON:

```bash
uv run audio-tools inspect my_song.wav --json
```

### 2. Separate Audio into Stems

Isolate the file into 4 stems (vocals, drums, bass, and other accompaniment):

```bash
uv run audio-tools separate my_song.wav -o ./output --stems 4
```

For autonomous agent execution, pass `--json` to direct diagnostic logs to `stderr` and print parseable JSON to `stdout`:

```bash
uv run audio-tools separate my_song.wav -o ./output --stems 4 --json
```

### 3. Verify Hardware Qualification

Before executing heavy batch workloads, run a pre-flight qualification check:

```bash
uv run audio-tools benchmark --json
```
