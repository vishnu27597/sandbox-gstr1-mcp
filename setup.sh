#!/bin/bash
# setup.sh — One-time setup for Sandbox GSTR-1 MCP Server
#
# Run this once after cloning the repository. It creates a local
# virtual environment (.venv) and installs all required packages.
# The run.sh script will automatically use this .venv.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=================================================="
echo " Sandbox GSTR-1 MCP Server — Setup"
echo "=================================================="
echo ""

# ── Find Python 3.11+
PYTHON=""
for candidate in python3.11 python3.12 python3.10 python3 python; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" --version 2>&1 | awk '{print $2}')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON=$(command -v "$candidate")
            echo "✓ Found Python $version at $PYTHON"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "✗ ERROR: Python 3.10 or higher is required but not found."
    echo "  Install it from https://www.python.org/downloads/ or via Homebrew:"
    echo "  brew install python@3.11"
    exit 1
fi

# ── Create virtual environment
echo ""
echo "Creating virtual environment at $VENV_DIR ..."
"$PYTHON" -m venv "$VENV_DIR"
echo "✓ Virtual environment created"

# ── Install dependencies
echo ""
echo "Installing dependencies ..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet
echo "✓ Dependencies installed"

# ── Verify MCP is importable
echo ""
echo "Verifying MCP server can start ..."
"$VENV_DIR/bin/python3" -c "from mcp.server.fastmcp import FastMCP; print('✓ MCP package OK')"

echo ""
echo "=================================================="
echo " Setup complete!"
echo "=================================================="
echo ""
echo "Next step — add this to your Claude Desktop config:"
echo ""
echo '  {
    "mcpServers": {
      "sandbox-gstr1": {
        "command": "'"$SCRIPT_DIR"'/run.sh",
        "env": {
          "SANDBOX_API_KEY": "key_test_ed6b10d21cf546d7b4b600021f91c341",
          "SANDBOX_API_SECRET": "secret_test_798d3274325741fab93dd24bbb786a3a"
        }
      }
    }
  }'
echo ""
echo "Config file location:"
echo "  macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "  Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo "  Linux:   ~/.config/Claude/claude_desktop_config.json"
echo ""
echo "Then fully restart Claude Desktop (Cmd+Q, then reopen)."
echo ""
