#!/usr/bin/env bash
set -eo pipefail

# Fail-fast wrapper for agent invocation
INPUT_FILE="${1:-}"
OUTPUT_DIR="${2:-output}"
STEMS="${3:-4}"
DEVICE="${4:-cpu}"

if [ -z "$INPUT_FILE" ]; then
    echo '{"status":"error","error_code":"ERR_MISSING_ARG","message":"Usage: separate.sh <input_file> [output_dir] [stems: 4|6] [device: cpu|auto]"}' >&2
    exit 1
fi

exec uv run audio-tools separate "$INPUT_FILE" --output-dir "$OUTPUT_DIR" --stems "$STEMS" --device "$DEVICE" --json
