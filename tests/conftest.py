import os
import tempfile

import numpy as np
import pytest
import soundfile as sf


@pytest.fixture
def sample_wav_path():
    """Generates a synthetic 1.0-second 44.1kHz stereo audio file for fast tests."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name

    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Generate 440Hz sine wave (stereo)
    left = 0.5 * np.sin(2 * np.pi * 440 * t)
    right = 0.5 * np.sin(2 * np.pi * 880 * t)
    audio = np.vstack((left, right)).T

    sf.write(path, audio, sample_rate, format="WAV", subtype="PCM_16")

    yield path

    if os.path.exists(path):
        os.remove(path)
