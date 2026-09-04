import json
import logging
import os
import sys

import click
import psutil
import torch

from audio_tools.engine.separator import separate_audio
from audio_tools.engine.telemetry import get_audio_metadata

logger = logging.getLogger("audio_tools")


def configure_cli_logging(json_mode: bool):
    """Configures logging: in json mode, suppress non-error logs to protect stdout."""
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    if json_mode:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """audio-tools: Deterministic audio manipulation and stem separation for AI agents."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("input_audio", type=str)
@click.option(
    "-o",
    "--output-dir",
    default="output",
    show_default=True,
    help="Directory or cloud URI prefix to write separated stem files.",
)
@click.option(
    "-s",
    "--stems",
    type=click.Choice(["4", "6"]),
    default="4",
    show_default=True,
    help="Number of stems: 4 (vocals, drums, bass, other) or 6 (+ guitar, piano).",
)
@click.option(
    "-d",
    "--device",
    type=click.Choice(["cpu", "auto"]),
    default="cpu",
    show_default=True,
    help="Execution device: 'cpu' (default, maximum stability) or 'auto' (detects mps/cuda).",
)
@click.option(
    "--json",
    "json_mode",
    is_flag=True,
    help="Emit strictly valid machine-readable JSON to stdout (Agent AX mode).",
)
@click.option(
    "--no-peaks",
    is_flag=True,
    help="Skip computing 100-point waveform visualization peaks.",
)
@click.option(
    "-t",
    "--threads",
    type=int,
    default=None,
    help="Number of CPU threads to allocate for inference.",
)
def separate(input_audio, output_dir, stems, device, json_mode, no_peaks, threads):
    """Separate an audio file into isolated vocal and instrument stems."""
    configure_cli_logging(json_mode)

    # Pre-flight check: RAM qualification
    try:
        vm = psutil.virtual_memory()
        available_gb = vm.available / (1024**3)
        if available_gb < 2.5:
            err_msg = (
                f"Low available memory warning: {available_gb:.1f}GB available. "
                f"HTDemucs requires >= 3.0GB to prevent out-of-memory termination."
            )
            if json_mode:
                click.echo(
                    json.dumps(
                        {
                            "status": "error",
                            "error_code": "ERR_LOW_MEMORY",
                            "message": err_msg,
                            "available_gb": round(available_gb, 2),
                        }
                    )
                )
                sys.exit(2)
            else:
                click.secho(f"WARNING: {err_msg}", fg="yellow", err=True)
    except Exception:
        pass

    try:
        if not json_mode:
            click.secho("Starting HTDemucs stem separation...", fg="cyan")
            click.echo(f"  Input:   {input_audio}")
            click.echo(f"  Output:  {output_dir}")
            click.echo(f"  Stems:   {stems}")
            click.echo(f"  Device:  {device}")

        result = separate_audio(
            input_audio=input_audio,
            output_dir=output_dir,
            stems_count=int(stems),
            device=device,
            extract_peaks=not no_peaks,
            threads=threads,
        )

        if json_mode:
            click.echo(result.model_dump_json(indent=2))
        else:
            click.secho("\nSeparation successfully completed!", fg="green", bold=True)
            click.echo("\nOutput Stems:")
            for stem_name, stem_path in result.stems.items():
                click.echo(f"  - {stem_name:8s}: {stem_path}")

            metrics = result.metrics
            click.echo("\nTelemetry:")
            click.echo(f"  - Audio Duration: {metrics.get('audio_duration_sec', 0):.1f}s")
            click.echo(f"  - Inference Time: {metrics.get('inference_time_sec', 0):.1f}s")
            click.echo(f"  - Real-Time Factor: {metrics.get('real_time_factor', 0)}")
            click.echo(f"  - Peak Memory:    {metrics.get('peak_rss_mb', 0):.1f} MB")
            click.echo(
                f"  - Device / Cores: {result.device} ({metrics.get('cpu_threads')} threads)"
            )

        sys.exit(0)

    except FileNotFoundError as fnf:
        if json_mode:
            click.echo(
                json.dumps(
                    {
                        "status": "error",
                        "error_code": "ERR_FILE_NOT_FOUND",
                        "message": str(fnf),
                    }
                )
            )
        else:
            click.secho(f"Error: {fnf}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        if json_mode:
            click.echo(
                json.dumps(
                    {
                        "status": "error",
                        "error_code": "ERR_INFERENCE_FAILED",
                        "message": str(e),
                    }
                )
            )
        else:
            click.secho(f"Separation failed: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_audio", type=str)
@click.option(
    "--json",
    "json_mode",
    is_flag=True,
    help="Emit machine-readable JSON to stdout.",
)
def inspect(input_audio, json_mode):
    """Inspect audio metadata (duration, sample rate, channels, format)."""
    configure_cli_logging(json_mode)

    if not os.path.exists(input_audio) and not input_audio.startswith("gs://"):
        err_obj = {"status": "error", "message": f"File not found: {input_audio}"}
        if json_mode:
            click.echo(json.dumps(err_obj))
        else:
            click.secho(err_obj["message"], fg="red", err=True)
        sys.exit(1)

    meta = get_audio_metadata(input_audio)
    if json_mode:
        click.echo(
            json.dumps({"status": "success", "file": input_audio, "metadata": meta}, indent=2)
        )
    else:
        click.secho(f"Audio Inspection: {input_audio}", fg="cyan", bold=True)
        for k, v in meta.items():
            click.echo(f"  {k:18s}: {v}")


@cli.command()
@click.option(
    "--json",
    "json_mode",
    is_flag=True,
    help="Emit machine-readable JSON to stdout.",
)
def benchmark(json_mode):
    """Benchmark and qualify host resources for audio inference."""
    configure_cli_logging(json_mode)

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

    if json_mode:
        click.echo(json.dumps(data, indent=2))
    else:
        click.secho("Host Audio Processing Benchmark Qualification", fg="cyan", bold=True)
        click.echo(f"  CPU Cores:              {cpu_count}")
        click.echo(f"  Available Memory:       {available_ram_gb} GB (Total: {total_ram_gb} GB)")
        click.echo(f"  Hardware Acceleration:  {detected_accel}")
        click.echo(f"  4-Stem Qualification:   {'PASSED' if qualifies_4s else 'WARN (Low RAM)'}")
        click.echo(f"  6-Stem Qualification:   {'PASSED' if qualifies_6s else 'WARN (Low RAM)'}")


@cli.command("download-models")
@click.option(
    "-m",
    "--model",
    type=click.Choice(["all", "4s", "6s"]),
    default="all",
    help="Select which models to pre-download: '4s' (htdemucs), '6s' (htdemucs_6s), or 'all'.",
)
def download_models(model):
    """Pre-cache Meta HTDemucs model configurations and weights for offline execution."""
    import demucs.api

    click.secho("Pre-caching official Meta HTDemucs model weights...", fg="cyan")

    if model in ("4s", "all"):
        click.echo("Fetching 4-stem model (htdemucs)...")
        demucs.api.Separator(model="htdemucs")
    if model in ("6s", "all"):
        click.echo("Fetching 6-stem model (htdemucs_6s)...")
        demucs.api.Separator(model="htdemucs_6s")

    click.secho("Model cache pre-warm complete.", fg="green")


if __name__ == "__main__":
    cli()
