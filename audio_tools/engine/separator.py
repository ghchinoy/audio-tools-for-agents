import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np
import soundfile as sf
import torch
from audio_separator.separator import Separator
from pydantic import BaseModel, Field

from audio_tools.engine.storage import (
    export_output_file,
    resolve_input_file,
)
from audio_tools.engine.telemetry import (
    PeakMemorySampler,
    calculate_rtf,
    get_audio_metadata,
    get_current_rss_mb,
)

logger = logging.getLogger(__name__)


def resolve_device(requested_device: str = "cpu") -> str:
    """Resolves the PyTorch execution device.

    Defaults strictly to 'cpu' for stability and predictability.
    If 'auto' is requested, checks CUDA first, then Apple Silicon MPS, then falls back to CPU.
    """
    requested = (requested_device or "cpu").lower().strip()
    if requested == "cpu":
        return "cpu"
    if requested == "auto":
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    if requested in ("cuda", "mps"):
        return requested
    return "cpu"


def configure_thread_pool(num_threads: Optional[int] = None) -> int:
    """Pins PyTorch and BLAS thread pools to prevent CPU starvation."""
    threads = num_threads or int(os.getenv("STEMMER_NUM_THREADS", str(os.cpu_count() or 4)))
    os.environ.setdefault("OMP_NUM_THREADS", str(threads))
    os.environ.setdefault("MKL_NUM_THREADS", str(threads))
    torch.set_num_threads(threads)
    return threads


def extract_waveform_peaks(audio_path: str, num_peaks: int = 100) -> list[float]:
    """Generates normalized waveform peak values for UI rendering."""
    try:
        data, _samplerate = sf.read(audio_path)
        if data.ndim > 1:
            # Average down to mono
            data = data.mean(axis=1)

        total_samples = len(data)
        if total_samples == 0:
            return [0.0] * num_peaks

        chunk_size = max(1, total_samples // num_peaks)
        peaks = []
        for i in range(num_peaks):
            start = i * chunk_size
            end = min(total_samples, (i + 1) * chunk_size)
            if start >= total_samples:
                peaks.append(0.0)
            else:
                chunk = data[start:end]
                peak = float(np.max(np.abs(chunk))) if len(chunk) > 0 else 0.0
                peaks.append(round(min(1.0, peak), 3))
        return peaks
    except Exception as e:
        logger.warning("Failed to extract peaks for %s: %s", audio_path, e)
        return []


class SeparationOutput(BaseModel):
    """Complete, machine-readable separation result."""

    status: str = "success"
    input_path: str
    output_dir: str
    stems_count: int
    model_name: str
    device: str
    stems: dict[str, str] = Field(default_factory=dict)
    peaks: dict[str, list[float]] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)


def separate_audio(
    input_audio: str,
    output_dir: str = "output",
    stems_count: int = 4,
    device: str = "cpu",
    model_dir: Optional[str] = None,
    extract_peaks: bool = True,
    threads: Optional[int] = None,
) -> SeparationOutput:
    """Separates an audio file into vocal and instrument stems using HTDemucs.

    Args:
        input_audio: Local file path or cloud URI (gs://).
        output_dir: Local destination directory or cloud URI prefix.
        stems_count: 4 (vocals, drums, bass, other) or 6 (adds guitar and piano).
        device: 'cpu' (default) or 'auto' (detects mps/cuda).
        model_dir: Directory where models are cached. Defaults to ~/.cache/audio-tools/models.
        extract_peaks: Whether to compute 100-point normalized waveform peaks for each stem.
        threads: Thread count for PyTorch CPU operations.

    Returns:
        SeparationOutput containing file locations, waveform peaks, and telemetry metrics.
    """
    active_device = resolve_device(device)
    active_threads = configure_thread_pool(threads)

    cache_dir = model_dir or os.path.expanduser("~/.cache/audio-tools/models")
    os.makedirs(cache_dir, exist_ok=True)

    model_name = "htdemucs_6s.yaml" if stems_count == 6 else "htdemucs.yaml"
    start_total = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="audio_tools_") as tmpdir:
        local_input = os.path.join(tmpdir, "source_input.wav")
        resolved_input = resolve_input_file(input_audio, local_input)

        separator_kwargs = {
            "output_dir": tmpdir,
            "model_file_dir": cache_dir,
        }

        if active_device == "cpu":
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
            torch.cuda.is_available = lambda: False
            if hasattr(torch.backends, "mps"):
                torch.backends.mps.is_available = lambda: False
                torch.backends.mps.is_built = lambda: False

        mem_before = get_current_rss_mb()
        start_inference = time.perf_counter()

        with PeakMemorySampler() as sampler:
            separator = Separator(**separator_kwargs)
            separator.load_model(model_name)
            output_filenames = separator.separate(resolved_input)

        inference_duration = time.perf_counter() - start_inference
        peak_rss = sampler.peak_mb

        # Map generated files to semantic stem categories
        stems_dict = {}
        peaks_dict = {}

        for fname in output_filenames:
            local_stem_path = os.path.join(tmpdir, fname)
            name_lower = fname.lower()

            if "(vocals)" in name_lower or "vocals" in name_lower:
                category = "vocals"
            elif "(drums)" in name_lower or "drums" in name_lower:
                category = "drums"
            elif "(bass)" in name_lower or "bass" in name_lower:
                category = "bass"
            elif "(guitar)" in name_lower or "guitar" in name_lower:
                category = "guitar"
            elif "(piano)" in name_lower or "piano" in name_lower:
                category = "piano"
            elif "(other)" in name_lower or "other" in name_lower:
                category = "other"
            else:
                category = Path(fname).stem

            # Export to desired destination
            final_dest = export_output_file(local_stem_path, output_dir)
            stems_dict[category] = final_dest

            if extract_peaks and os.path.exists(local_stem_path):
                peaks_dict[category] = extract_waveform_peaks(local_stem_path, num_peaks=100)

        meta = get_audio_metadata(resolved_input)
        rtf = calculate_rtf(inference_duration, meta["duration_sec"])
        total_duration = time.perf_counter() - start_total

        metrics = {
            "model_name": model_name,
            "stems_count": stems_count,
            "device": active_device,
            "cpu_threads": active_threads,
            "audio_duration_sec": meta["duration_sec"],
            "samplerate": meta["samplerate"],
            "channels": meta["channels"],
            "file_size_mb": meta["file_size_mb"],
            "inference_time_sec": round(inference_duration, 2),
            "total_time_sec": round(total_duration, 2),
            "real_time_factor": rtf,
            "peak_rss_mb": round(peak_rss, 2),
            "memory_delta_mb": round(peak_rss - mem_before, 2),
        }

        logger.info("Separation complete: %s", json.dumps(metrics))

        return SeparationOutput(
            status="success",
            input_path=input_audio,
            output_dir=output_dir,
            stems_count=stems_count,
            model_name=model_name,
            device=active_device,
            stems=stems_dict,
            peaks=peaks_dict,
            metrics=metrics,
        )
