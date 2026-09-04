# Agent Instructions for `audio-tools-for-agents`

## Project Overview

`audio-tools-for-agents` is an agent-native audio processing and stem separation library. It is designed to be used by autonomous agents via CLI (`--json`), Model Context Protocol (MCP), Agent Skills, and Agent Plugins.

## Primary Tooling & Verification

* Package Manager: `uv`
* Python Version: `>=3.11, <3.14` (CPython 3.13)
* Linter & Formatter: `ruff`
* Test Framework: `pytest`

### Essential Commands

```bash
# Install / sync dependencies
make setup          # or: uv sync

# Run tests
make test           # or: uv run pytest tests -v

# Run lint and format checks
make lint           # or: uv run ruff check . && uv run ruff format --check .

# Auto-format
make format         # or: uv run ruff check --fix . && uv run ruff format .

# Validate Agent Plugins and Agent Skills specification conformance
make validate-spec

# Run MCP server locally over stdio
make mcp
```

## Architectural Rules

1. **CPU Default:** All audio separation operations must default to CPU execution (`device="cpu"`) for universal host compatibility. Never make GPU acceleration mandatory.
2. **Context Protection:** Never emit raw audio bytes or massive arrays to `stdout`. Always output file paths and summary telemetry.
3. **Agent AX Mode:** In the CLI, the `--json` flag must always produce valid, single-object JSON on `stdout`. All logs, warnings, or debug statements must be routed to `stderr`.
4. **Editorial Standard:** Prose documentation must adhere to the project house style. Avoid em dashes in markdown prose text; use commas, colons, periods, or parentheses instead.
5. **Spec Conformance:** Any modification to `plugin.json`, `mcp.json`, or `SKILL.md` must pass `make validate-spec`.
