---
title: Agent Skills Specification
description: Progressive-disclosure skill package for coding agents.
---

The `audio-stemming` skill complies with the open [Agent Skills Specification](https://agentskills.io).

## Three-Stage Progressive Disclosure

1. **Discovery Stage:** At agent startup, only the YAML frontmatter name and description are ingested into context. Because the description is constrained to 278 characters, agents retain this capability with negligible token overhead.
2. **Activation Stage:** When a prompt matches the skill's capabilities (e.g., "isolate vocals from track.wav"), the agent loads the full instructions from `SKILL.md`.
3. **Execution Stage:** The agent follows the structured instructions, referencing the decision matrix and invoking bundled runner scripts.

## Skill Package Structure

```text
plugins/audio-stemming/skills/audio-stemming/
├── SKILL.md                          # Frontmatter + operational instructions
├── scripts/
│   ├── separate.sh                   # Non-interactive CLI wrapper
│   └── benchmark.py                  # Host qualification checker
├── references/
│   ├── stemmer-matrix.md             # Model trade-offs and memory ceilings
│   └── error-catalog.md              # Actionable remediation codes
└── assets/
    └── sample_meta.json              # Sample telemetry output schema
```

## Frontmatter Metadata

```yaml
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
```
