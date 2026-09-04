import json
from unittest.mock import patch

from click.testing import CliRunner

from audio_tools.cli import cli
from audio_tools.engine.separator import SeparationOutput


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "audio-tools" in result.output
    assert "separate" in result.output
    assert "inspect" in result.output
    assert "benchmark" in result.output


def test_cli_inspect_json(sample_wav_path):
    runner = CliRunner()
    result = runner.invoke(cli, ["inspect", sample_wav_path, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "success"
    assert data["metadata"]["channels"] == 2
    assert data["metadata"]["samplerate"] == 44100


def test_cli_benchmark_json():
    runner = CliRunner()
    result = runner.invoke(cli, ["benchmark", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "success"
    assert "cpu_cores" in data
    assert "available_ram_gb" in data
    assert data["recommended_default_device"] == "cpu"


@patch("audio_tools.cli.separate_audio")
def test_cli_separate_json(mock_separate, sample_wav_path):
    mock_separate.return_value = SeparationOutput(
        status="success",
        input_path=sample_wav_path,
        output_dir="output",
        stems_count=4,
        model_name="htdemucs",
        device="cpu",
        stems={
            "vocals": "output/sample_(Vocals)_htdemucs.wav",
            "drums": "output/sample_(Drums)_htdemucs.wav",
        },
        peaks={"vocals": [0.1, 0.5], "drums": [0.2, 0.8]},
        metrics={"real_time_factor": 0.42, "inference_time_sec": 12.0},
    )

    runner = CliRunner()
    result = runner.invoke(
        cli, ["separate", sample_wav_path, "-o", "output", "--stems", "4", "--json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "success"
    assert "vocals" in data["stems"]
    assert data["metrics"]["real_time_factor"] == 0.42


def test_cli_inspect_missing_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["inspect", "nonexistent.wav", "--json"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["status"] == "error"


def test_separate_sh_out_of_tree(tmp_path):
    import subprocess
    from pathlib import Path

    script = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "audio-stemming"
        / "scripts"
        / "separate.sh"
    )
    result = subprocess.run([str(script)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "ERR_MISSING_ARG" in result.stderr
