from audio_tools.engine.separator import extract_waveform_peaks, resolve_device
from audio_tools.engine.telemetry import (
    PeakMemorySampler,
    calculate_rtf,
    get_audio_metadata,
    get_current_rss_mb,
)


def test_resolve_device():
    assert resolve_device("cpu") == "cpu"
    assert resolve_device("") == "cpu"
    assert resolve_device("CPU") == "cpu"
    # Auto resolves to a valid string (cpu, mps, or cuda)
    auto_dev = resolve_device("auto")
    assert auto_dev in ("cpu", "mps", "cuda")


def test_calculate_rtf():
    assert calculate_rtf(50.0, 100.0) == 0.5
    assert calculate_rtf(120.0, 60.0) == 2.0
    assert calculate_rtf(10.0, 0.0) == 0.0


def test_get_current_rss_mb():
    rss = get_current_rss_mb()
    assert isinstance(rss, float)
    assert rss > 0.0


def test_peak_memory_sampler():
    with PeakMemorySampler(interval_sec=0.05) as sampler:
        # Allocate a small block to induce memory activity
        _arr = [0] * 1000000
    assert sampler.peak_mb > 0.0


def test_get_audio_metadata(sample_wav_path):
    meta = get_audio_metadata(sample_wav_path)
    assert meta["channels"] == 2
    assert meta["samplerate"] == 44100
    assert 0.9 <= meta["duration_sec"] <= 1.1
    assert meta["format"] == "WAV"


def test_extract_waveform_peaks(sample_wav_path):
    peaks = extract_waveform_peaks(sample_wav_path, num_peaks=50)
    assert len(peaks) == 50
    assert all(0.0 <= p <= 1.0 for p in peaks)
    assert max(peaks) > 0.1
