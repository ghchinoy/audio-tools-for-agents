#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

# Walk upwards to locate repository root
search_dir = Path(__file__).resolve().parent
repo_root = None
for parent in [search_dir, *search_dir.parents]:
    if (parent / "pyproject.toml").exists() and (parent / "audio_tools").is_dir():
        repo_root = parent
        break

# Resolve execution command with multi-tier fallback
if shutil.which("audio-tools"):
    cmd = ["audio-tools", "benchmark", "--json"]
elif repo_root and (repo_root / ".venv" / "bin" / "audio-tools").is_file():
    cmd = [str(repo_root / ".venv" / "bin" / "audio-tools"), "benchmark", "--json"]
elif repo_root:
    cmd = ["uv", "run", "--project", str(repo_root), "audio-tools", "benchmark", "--json"]
else:
    cmd = ["uv", "run", "audio-tools", "benchmark", "--json"]

proc = subprocess.run(cmd)
sys.exit(proc.returncode)
