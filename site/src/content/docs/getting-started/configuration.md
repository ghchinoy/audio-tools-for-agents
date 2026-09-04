---
title: Configuration & Hardware
description: Configuring thread pools, execution devices, and memory settings.
---

## Device Execution Strategy

By default, `audio-tools` enforces multi-threaded CPU inference (`device="cpu"`). 

Deep learning stem separation on consumer GPUs frequently encounters CUDA out-of-memory errors on long audio files. CPU execution guarantees reliable behavior across diverse container environments, developer laptops, and virtual machines.

### Hardware Acceleration (`--device auto`)

When hardware acceleration is explicitly requested:

```bash
uv run audio-tools separate my_song.wav -d auto
```

The engine resolves devices using this priority sequence:
1. **NVIDIA CUDA (`cuda`):** Used if PyTorch detects functional CUDA drivers.
2. **Apple Silicon Metal (`mps`):** Used if running on macOS with Apple Silicon GPU support.
3. **Multi-Threaded CPU (`cpu`):** Fallback if accelerated backends are unavailable.

## Thread Pool Pinning

To avoid saturating all host CPU cores during separation, `audio-tools` pins PyTorch and underlying BLAS thread pools.

Configure the active thread count using the `STEMMER_NUM_THREADS` environment variable or the CLI `--threads` flag:

```bash
export STEMMER_NUM_THREADS=4
uv run audio-tools separate my_song.wav --threads 4
```

When unset, the engine defaults to the detected physical CPU core count, or 4 threads.

## Pre-Caching Model Weights

To run offline in disconnected environments or container builds, pre-warm the model cache:

```bash
# Pre-download both 4-stem and 6-stem models
uv run audio-tools download-models --model all
```

Model weights are cached in `~/.cache/audio-tools/models` by default.
