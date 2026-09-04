import logging
import os
import resource
import sys
import threading
from typing import Any, Optional

import psutil
import soundfile as sf

logger = logging.getLogger(__name__)


def get_current_rss_mb() -> float:
    """Returns the process's current resident set size (RSS) in megabytes."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    kb = int(line.split()[1])
                    return kb / 1024.0
    except (FileNotFoundError, OSError):
        pass

    try:
        proc = psutil.Process()
        return proc.memory_info().rss / (1024.0 * 1024.0)
    except Exception:
        pass

    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return usage / (1024.0 * 1024.0)  # macOS ru_maxrss is in bytes
    return usage / 1024.0  # Linux ru_maxrss is in kilobytes


class PeakMemorySampler:
    """Tracks the true peak RSS for a single task by polling on a background thread.

    Usage:
        with PeakMemorySampler() as sampler:
            do_work()
        peak = sampler.peak_mb
    """

    def __init__(self, interval_sec: float = 0.1):
        self._interval = interval_sec
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.peak_mb: float = 0.0

    def _sample(self) -> None:
        try:
            current = get_current_rss_mb()
            if current > self.peak_mb:
                self.peak_mb = current
        except Exception:
            logger.debug("PeakMemorySampler: failed to sample RSS", exc_info=True)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._sample()
            self._stop_event.wait(self._interval)

    def __enter__(self) -> "PeakMemorySampler":
        self.peak_mb = get_current_rss_mb()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc_info) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self._sample()


def get_audio_metadata(file_path: str) -> dict[str, Any]:
    """Extracts duration, sample rate, channels, and file size for audio input."""
    try:
        info = sf.info(file_path)
        size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
        return {
            "duration_sec": round(info.duration, 2),
            "samplerate": info.samplerate,
            "channels": info.channels,
            "format": info.format,
            "subtype": info.subtype,
            "file_size_mb": size_mb,
        }
    except Exception as e:
        logger.warning("Could not inspect audio metadata for %s: %s", file_path, e)
        size_mb = (
            round(os.path.getsize(file_path) / (1024 * 1024), 2)
            if os.path.exists(file_path)
            else 0.0
        )
        return {
            "duration_sec": 0.0,
            "samplerate": 0,
            "channels": 0,
            "format": "unknown",
            "subtype": "unknown",
            "file_size_mb": size_mb,
        }


def calculate_rtf(inference_time_sec: float, audio_duration_sec: float) -> float:
    """Calculates Real-Time Factor (RTF = inference_duration / audio_duration)."""
    if audio_duration_sec <= 0:
        return 0.0
    return round(inference_time_sec / audio_duration_sec, 3)
