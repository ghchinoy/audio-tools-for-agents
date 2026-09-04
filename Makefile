.PHONY: help setup test lint format mcp validate-spec build-docs dev-docs clean

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install dependencies using uv and npm
	uv sync
	cd site && npm install

test: ## Run pytest test suite
	uv run pytest tests -v

lint: ## Check linting and formatting with ruff
	uv run ruff check .
	uv run ruff format --check .

format: ## Automatically fix lint and format issues with ruff
	uv run ruff check --fix .
	uv run ruff format .

build-docs: ## Build the Catppuccin Astro Starlight documentation site
	cd site && npm run build

dev-docs: ## Start the Starlight local documentation dev server
	cd site && npm run dev

mcp: ## Start stdio FastMCP server
	uv run python -m audio_tools.mcp_server

validate-spec: ## Validate Agent Plugins and Agent Skills spec conformance
	/Users/ghchinoy/projects/agent-skills/plugins/agent-plugin-authoring/skills/skills-to-plugins/scripts/validate-plugins.sh

clean: ## Remove temporary outputs and caches
	rm -rf output/ temp/ .pytest_cache/ .ruff_cache/ build/ dist/ site/dist/ site/.astro/
