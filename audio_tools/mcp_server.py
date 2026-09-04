import json
import os

import psutil
import torch
from mcp.server.fastmcp import FastMCP

from audio_tools.engine.separator import separate_audio
from audio_tools.engine.telemetry import get_audio_metadata

mcp = FastMCP("audio-tools")


@mcp.tool()
def inspect_audio(file_path: str) -> str:
    """Inspects audio metadata for a given local file or cloud URI.

    Args:
        file_path: The local file path (e.g. /path/to/song.wav) or cloud URI (gs://...)

    Returns:
        JSON string containing duration_sec, samplerate, channels, format, and file_size_mb.
    """
    if not os.path.exists(file_path) and not file_path.startswith("gs://"):
        return json.dumps(
            {
                "status": "error",
                "error_code": "ERR_FILE_NOT_FOUND",
                "message": f"File not found: {file_path}",
            }
        )
    meta = get_audio_metadata(file_path)
    return json.dumps({"status": "success", "file": file_path, "metadata": meta}, indent=2)


@mcp.tool()
def benchmark_system() -> str:
    """Evaluates host system hardware to determine stem separation viability.

    Returns:
        JSON string with CPU core count, available RAM, detected acceleration (CUDA/MPS),
        and model qualification verdicts.
    """
    cpu_count = os.cpu_count() or 1
    vm = psutil.virtual_memory()
    total_ram_gb = round(vm.total / (1024**3), 2)
    available_ram_gb = round(vm.available / (1024**3), 2)

    cuda_avail = torch.cuda.is_available()
    mps_avail = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()

    detected_accel = "none (cpu)"
    if cuda_avail:
        detected_accel = f"cuda ({torch.cuda.get_device_name(0)})"
    elif mps_avail:
        detected_accel = "mps (Apple Silicon GPU)"

    qualifies_4s = available_ram_gb >= 2.5
    qualifies_6s = available_ram_gb >= 3.5

    data = {
        "status": "success",
        "cpu_cores": cpu_count,
        "total_ram_gb": total_ram_gb,
        "available_ram_gb": available_ram_gb,
        "hardware_acceleration": detected_accel,
        "recommended_default_device": "cpu",
        "qualifies_4_stem": qualifies_4s,
        "qualifies_6_stem": qualifies_6s,
    }
    return json.dumps(data, indent=2)


@mcp.tool()
def separate_stems(
    input_path: str,
    output_dir: str = "output",
    stems_count: int = 4,
    device: str = "cpu",
) -> str:
    """Separates a mixed audio track into discrete vocal and instrumental stems using HTDemucs.

    Args:
        input_path: Local file path or cloud URI of the input audio file (WAV, MP3, etc.).
        output_dir: Destination directory or cloud URI prefix to write the separated stem files.
        stems_count: Number of stems to extract: 4 (vocals, drums, bass, other) or 6 (+ guitar, piano).
        device: PyTorch device. Defaults to 'cpu' for stability; pass 'auto' for hardware acceleration.

    Returns:
        JSON string containing the output paths for each stem, waveform peaks, and telemetry metrics.
    """
    try:
        result = separate_audio(
            input_audio=input_path,
            output_dir=output_dir,
            stems_count=stems_count,
            device=device,
            extract_peaks=True,
        )
        return result.model_dump_json(indent=2)
    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "error_code": "ERR_SEPARATION_FAILED",
                "message": str(e),
            },
            indent=2,
        )


if __name__ == "__main__":
    mcp.run()
