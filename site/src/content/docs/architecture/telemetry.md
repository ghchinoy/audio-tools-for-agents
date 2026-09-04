---
title: Memory & Telemetry
description: Live peak RSS polling, Real-Time Factor (RTF) calculations, and hardware qualification.
---

## Live Peak Memory Sampling

Standard operating system utilities such as `resource.getrusage` only report process-lifetime high-water marks (`ru_maxrss`). 

When an agent executes multiple audio operations in a single session or long-lived container, subsequent operations report the previous high-water mark rather than their own memory consumption. This obscures memory spikes and memory leaks.

### The `PeakMemorySampler` Thread

`audio-tools` includes a background polling thread that samples resident set size every 100 milliseconds throughout the separation run:
* **Linux Hosts:** Directly queries `/proc/self/status` for the live `VmRSS` value.
* **macOS Workstations:** Queries system process memory descriptors.

This records accurate task-specific metrics:
* `peak_rss_mb`: Peak resident set size observed during this specific operation.
* `memory_delta_mb`: Difference between peak memory and baseline memory at task start.

## Real-Time Factor ($RTF$)

The Real-Time Factor measures compute throughput relative to audio duration:

$$RTF = \frac{\text{Inference Duration (seconds)}}{\text{Audio Duration (seconds)}}$$

* An $RTF < 1.0$ indicates that inference runs faster than real-time playback.
* A standard 3-minute song ($180\text{s}$) processed on an 8-core CPU typically achieves an $RTF$ between $0.35$ and $0.55$, completing in under 90 seconds.
