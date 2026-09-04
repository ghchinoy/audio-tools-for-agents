# HTDemucs Model Selection Matrix

| Dimension | 4-Stem Model (`htdemucs.yaml`) | 6-Stem Model (`htdemucs_6s.yaml`) |
| :--- | :--- | :--- |
| **Output Stems** | Vocals, Drums, Bass, Other | Vocals, Drums, Bass, Other, Guitar, Piano |
| **Target Use Cases** | Vocal removal, karaoke, acapella extraction, rhythm section sampling | Detailed multitrack remixing, acoustic guitar or piano isolation |
| **Recommended RAM** | $\ge 3.0\text{ GB}$ available | $\ge 4.0\text{ GB}$ available |
| **Peak RSS (CPU)** | $\sim 2.2\text{ GB} - 2.6\text{ GB}$ | $\sim 2.8\text{ GB} - 3.4\text{ GB}$ |
| **Real-Time Factor (RTF)** | $0.35 - 0.55$ (Faster than real-time on modern 8-core CPU) | $0.60 - 0.95$ |
| **Model Size on Disk** | $\sim 80\text{ MB}$ | $\sim 120\text{ MB}$ |
| **CLI Flag** | `--stems 4` | `--stems 6` |
| **MCP Param** | `"stems_count": 4` | `"stems_count": 6` |

## Resource Guidance

1. **CPU Threading:**
   The engine pins thread usage to `STEMMER_NUM_THREADS` (or detected CPU core count). Allocating 4-8 threads provides optimal scaling before memory bandwidth saturates.
2. **Apple Silicon (MPS):**
   Using `--device auto` on M-series chips routes tensor operations to the Unified Memory GPU, reducing inference duration by roughly 40-50% compared to pure CPU.
