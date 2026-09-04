# Architecture Specification: Audio Tools for Agents

## 1. System Intent & Ecosystem Role

`audio-tools-for-agents` provides deterministic, non-cloud audio processing primitives for autonomous coding agents and automated media pipelines.

While cloud foundation models (such as Gemini) excel at semantic audio perception and generative composition, deep-learning signal separation requires dedicated neural network inference operating directly over raw audio waveforms. This repository isolates and standardizes that capability using Meta's HTDemucs (Hybrid Transformer Demucs) architecture.

The package exposes four distinct delivery surfaces:
1. **Agent-Aware CLI (`audio-tools`):** Dual-mode execution supporting both human developer ergonomics and agent automation via the `--json` flag.
2. **Model Context Protocol (MCP) Server (`audio_tools.mcp_server`):** Standardized stdio JSON-RPC tool interface for LLM agent runtimes.
3. **Agent Skill (`audio-stemming`):** Progressive-disclosure instructions and operational rubrics complying with the `agentskills.io` standard.
4. **Agent Plugin (`audio-tools`):** Portable package manifest conforming to the Agent Plugins v1.0.0 specification.

---

## 2. Audio Separation Engine & Model Selection

### 2.1 The HTDemucs Architecture

Audio separation decomposes an arbitrary mixed waveform $x(t) \in \mathbb{R}^{C \times T}$ into $K$ independent constituent sources:

$$x(t) = \sum_{k=1}^{K} s_k(t)$$

HTDemucs operates across dual representations: a time-domain convolutional U-Net cross-connected with a frequency-domain spectrogram transformer. This hybrid formulation produces high acoustic fidelity, preserving transient percussive attacks while minimizing phase cancellation artifacts.

Two model configurations are supported:

* **Standard 4-Stem (`htdemucs.yaml`):** Isolates Vocals, Drums, Bass, and Other. Suited for vocal extraction, sampling, and karaoke tracks.
* **Pro 6-Stem (`htdemucs_6s.yaml`):** Isolates Vocals, Drums, Bass, Other, Guitar, and Piano. Suited for multitrack remixing and acoustic instrument transcription.

### 2.2 Execution Device Strategy

By default, the engine enforces CPU-only execution (`device="cpu"`). 

Deep-learning audio separation on consumer GPUs often encounters out-of-memory errors due to long waveform sequences. CPU execution guarantees predictable behavior across heterogeneous container hosts, developer laptops, and virtual machines without specialized driver dependencies.

When hardware acceleration is explicitly requested (`device="auto"`):
1. The engine checks for NVIDIA CUDA availability.
2. If CUDA is absent, it checks for Apple Silicon Metal Performance Shaders (`mps`).
3. If neither accelerated backend is functional, it falls back to multi-threaded CPU execution.

---

## 3. Memory Profile & Live Telemetry

### 3.1 Peak Memory Sampling

Standard process accounting (`resource.getrusage`) records a lifetime high-water mark (`ru_maxrss`). When an agent or worker container processes multiple audio tracks in sequence, lifetime high-water tracking reports stale metrics for subsequent jobs, concealing memory leaks.

To solve this, `PeakMemorySampler` runs a lightweight polling thread at 100ms intervals throughout the separation lifecycle. On Linux platforms, it inspects `/proc/self/status` for live `VmRSS` values. This provides true per-task peak memory telemetry (`peak_rss_mb`) and task memory delta (`memory_delta_mb`).

### 3.2 Thread Pool Pinning

Unconstrained PyTorch inference can saturate all available logical cores, degrading responsiveness on shared hosts. The engine reads the `STEMMER_NUM_THREADS` environment variable (defaulting to the detected physical CPU count or 4), pinning both PyTorch and underlying BLAS thread pools:

```python
torch.set_num_threads(active_threads)
os.environ["OMP_NUM_THREADS"] = str(active_threads)
os.environ["MKL_NUM_THREADS"] = str(active_threads)
```

---

## 4. Storage & Payload Boundaries

Processing uncompressed PCM WAV files creates significant I/O throughput. A standard three-minute stereo track at 44.1 kHz generates approximately 30 MB of input data and over 120 MB of separated stem audio.

The storage abstraction (`audio_tools.engine.storage`) resolves both local filesystem paths and remote Google Cloud Storage URIs (`gs://`):
1. **Local Filesystem:** Operates in-place or writes to the target directory.
2. **Cloud URIs:** Downloads the source object into an isolated temporary folder (`tempfile.TemporaryDirectory`), runs local separation, and streams resulting stems back to the destination cloud prefix with exponential backoff retries.

This prevents passing raw binary audio payloads through agent context windows or HTTP REST payloads, preserving LLM token capacity and respecting API payload limits.

---

## 5. Delivery Surface Protocols

### 5.1 Dual-Mode CLI Contract

The command-line interface implements the Agent-Aware CLI design guidelines:
* **Human Developer Mode:** Displays styled terminal banners, progress indications, and summary tables.
* **Agent Automation Mode (`--json`):** Directs all diagnostic logs to `stderr` and emits a single, strictly valid JSON object to `stdout`.

Exit codes indicate unambiguous operational status:
* `0`: Separation completed successfully.
* `1`: Input error or missing audio file.
* `2`: Insufficient memory (host available RAM below 2.5 GB).

### 5.2 FastMCP Server Integration

The MCP server exposes tool definitions using standard JSON-RPC over `stdio`. Agents invoke `separate_stems`, `inspect_audio`, or `benchmark_system` without managing shell subprocesses directly. 

The `mcp.json` manifest relies on the normative `${PLUGIN_ROOT}` token expansion:

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

This guarantees that the MCP server runs with its isolated `uv` virtual environment regardless of where the agent invokes it from.
