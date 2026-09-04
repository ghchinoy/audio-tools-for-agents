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

# Dynamically locate repository root containing audio_tools
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SEARCH_DIR="$SCRIPT_DIR"
REPO_ROOT=""

while [ "$SEARCH_DIR" != "/" ]; do
    if [ -f "$SEARCH_DIR/pyproject.toml" ] && [ -d "$SEARCH_DIR/audio_tools" ]; then
        REPO_ROOT="$SEARCH_DIR"
        break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

# Resolve execution binary with multi-tier fallback
if command -v audio-tools >/dev/null 2>&1; then
    AUDIO_BIN="audio-tools"
elif [ -n "$REPO_ROOT" ] && [ -x "${REPO_ROOT}/.venv/bin/audio-tools" ]; then
    AUDIO_BIN="${REPO_ROOT}/.venv/bin/audio-tools"
elif [ -n "$REPO_ROOT" ]; then
    AUDIO_BIN="uv run --project ${REPO_ROOT} audio-tools"
else
    AUDIO_BIN="uv run audio-tools"
fi

exec $AUDIO_BIN separate "$INPUT_FILE" --output-dir "$OUTPUT_DIR" --stems "$STEMS" --device "$DEVICE" --json
