#!/usr/bin/env bash
set -eo pipefail

echo "================================================================="
echo " audio-tools-for-agents: 1-Command Agent & CLI Installer"
echo "================================================================="
echo ""

# 1. Verify or Install uv
if ! command -v uv >/dev/null 2>&1; then
    echo "==> 'uv' not found. Installing uv (Astral)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

echo "==> Found uv: $(uv --version)"

# 2. Setup Plugin Directory
REPO_URL="https://github.com/ghchinoy/audio-tools-for-agents.git"
INSTALL_DIR="$HOME/.gemini/config/plugins/audio-tools-for-agents"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "==> Updating existing installation in $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    echo "==> Cloning repository into $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# 3. Synchronize Dependencies & Pre-cache Model
echo "==> Synchronizing Python virtual environment..."
(cd "$INSTALL_DIR" && uv sync)

# 4. Install Global CLI Binary via uv tool
echo "==> Installing global 'audio-tools' binary into ~/.local/bin..."
uv tool install "$INSTALL_DIR" --force

# 5. Link Skills for Antigravity & Claude Code
echo "==> Linking 'audio-stemming' skill for agent discovery..."
mkdir -p "$HOME/.gemini/config/skills" "$HOME/.claude/skills"
ln -sf "$INSTALL_DIR/skills/audio-stemming" "$HOME/.gemini/config/skills/audio-stemming"
ln -sf "$INSTALL_DIR/skills/audio-stemming" "$HOME/.claude/skills/audio-stemming"

echo ""
echo "✅ Installation complete!"
echo "   - CLI available at:      $(which audio-tools || echo '~/.local/bin/audio-tools')"
echo "   - Antigravity Skill at:  $HOME/.gemini/config/skills/audio-stemming"
echo "   - Claude Code Skill at:  $HOME/.claude/skills/audio-stemming"
echo ""
echo "Try it now: audio-tools benchmark"
