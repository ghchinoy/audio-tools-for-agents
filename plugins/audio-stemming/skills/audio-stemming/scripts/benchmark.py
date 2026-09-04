#!/usr/bin/env python3
import sys

from audio_tools.cli import benchmark

if __name__ == "__main__":
    sys.exit(benchmark(json_mode=True))
