---
title: Model Selection Matrix
description: Comparison of 4-stem and 6-stem HTDemucs configurations.
---

## Model Profiles

| Dimension | 4-Stem Model (`htdemucs`) | 6-Stem Model (`htdemucs_6s`) |
| :--- | :--- | :--- |
| **Output Stems** | Vocals, Drums, Bass, Other | Vocals, Drums, Bass, Other, Guitar, Piano |
| **Target Use Cases** | Vocal removal, karaoke, acapella extraction, rhythm sampling | Multitrack remixing, acoustic guitar isolation, piano transcription |
| **Recommended RAM** | $\ge 3.0\text{ GB}$ available | $\ge 4.0\text{ GB}$ available |
| **Peak RSS (CPU)** | $\sim 2.2\text{ GB} - 2.6\text{ GB}$ | $\sim 2.8\text{ GB} - 3.4\text{ GB}$ |
| **Real-Time Factor (RTF)** | $0.35 - 0.55$ | $0.60 - 0.95$ |
| **Model Size on Disk** | $\sim 80\text{ MB}$ | $\sim 120\text{ MB}$ |
| **CLI Flag** | `--stems 4` | `--stems 6` |
| **MCP Parameter** | `"stems_count": 4` | `"stems_count": 6` |

## Model Checkpoint Caching

Models are downloaded on first invocation and stored locally:
* Default directory: `~/.cache/audio-tools/models`
* Download weights explicitly: `uv run audio-tools download-models --model all`
