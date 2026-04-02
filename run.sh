#!/bin/bash
# run.sh — Launch wrapper for Sandbox GSTR-1 MCP Server
#
# Claude Desktop spawns this process directly without a login shell,
# so PATH, pyenv, conda, and virtualenv activations are NOT available.
# This script resolves the correct Python interpreter explicitly.

# ── Resolve the project directory (works regardless of where this is called from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Try to find Python in common macOS locations, in order of preference
PYTHON=""

# 1. Virtual environment inside the project (most reliable)
if [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python3"

# 2. pyenv shim
elif [ -f "$HOME/.pyenv/shims/python3" ]; then
    PYTHON="$HOME/.pyenv/shims/python3"

# 3. Homebrew Python (Apple Silicon)
elif [ -f "/opt/homebrew/bin/python3" ]; then
    PYTHON="/opt/homebrew/bin/python3"

# 4. Homebrew Python (Intel Mac)
elif [ -f "/usr/local/bin/python3" ]; then
    PYTHON="/usr/local/bin/python3"

# 5. System Python 3
elif [ -f "/usr/bin/python3" ]; then
    PYTHON="/usr/bin/python3"

# 6. Fallback — let the shell find it
else
    PYTHON="python3"
fi

# ── Log which Python is being used (goes to stderr, not stdout)
echo "[run.sh] Using Python: $PYTHON" >&2
echo "[run.sh] Project dir: $SCRIPT_DIR" >&2

# ── Pass through environment variables set by Claude Desktop
export SANDBOX_API_KEY="${SANDBOX_API_KEY:-key_test_ed6b10d21cf546d7b4b600021f91c341}"
export SANDBOX_API_SECRET="${SANDBOX_API_SECRET:-secret_test_798d3274325741fab93dd24bbb786a3a}"

# ── Run the server
exec "$PYTHON" "$SCRIPT_DIR/server.py"
