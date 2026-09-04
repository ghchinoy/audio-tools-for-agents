import json
from unittest.mock import patch

from audio_tools.engine.separator import SeparationOutput
from audio_tools.mcp_server import benchmark_system, inspect_audio, separate_stems


def test_mcp_inspect_audio(sample_wav_path):
    output_str = inspect_audio(sample_wav_path)
    data = json.loads(output_str)
    assert data["status"] == "success"
    assert data["metadata"]["channels"] == 2
    assert data["metadata"]["samplerate"] == 44100


def test_mcp_inspect_audio_missing():
    output_str = inspect_audio("/nonexistent/file.wav")
    data = json.loads(output_str)
    assert data["status"] == "error"
    assert data["error_code"] == "ERR_FILE_NOT_FOUND"


def test_mcp_benchmark_system():
    output_str = benchmark_system()
    data = json.loads(output_str)
    assert data["status"] == "success"
    assert "cpu_cores" in data
    assert "available_ram_gb" in data


@patch("audio_tools.mcp_server.separate_audio")
def test_mcp_separate_stems(mock_separate, sample_wav_path):
    mock_separate.return_value = SeparationOutput(
        status="success",
        input_path=sample_wav_path,
        output_dir="output",
        stems_count=4,
        model_name="htdemucs.yaml",
        device="cpu",
        stems={"vocals": "output/vocals.wav"},
        peaks={"vocals": [0.1, 0.2]},
        metrics={"inference_time_sec": 5.0},
    )

    output_str = separate_stems(
        input_path=sample_wav_path,
        output_dir="output",
        stems_count=4,
        device="cpu",
    )
    data = json.loads(output_str)
    assert data["status"] == "success"
    assert data["stems"]["vocals"] == "output/vocals.wav"
