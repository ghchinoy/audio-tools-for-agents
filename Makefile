.PHONY: help setup test lint format mcp validate-spec clean

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install dependencies using uv
	uv sync

test: ## Run pytest test suite
	uv run pytest tests -v

lint: ## Check linting and formatting with ruff
	uv run ruff check .
	uv run ruff format --check .

format: ## Automatically fix lint and format issues with ruff
	uv run ruff check --fix .
	uv run ruff format .

mcp: ## Start stdio FastMCP server
	uv run python -m audio_tools.mcp_server

validate-spec: ## Validate Agent Plugins and Agent Skills spec conformance
	/Users/ghchinoy/projects/agent-skills/plugins/agent-plugin-authoring/skills/skills-to-plugins/scripts/validate-plugins.sh

clean: ## Remove temporary outputs and caches
	rm -rf output/ temp/ .pytest_cache/ .ruff_cache/ build/ dist/
