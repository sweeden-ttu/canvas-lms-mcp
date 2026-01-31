#!/usr/bin/env bash
# Interactive loop: add MCP servers as git submodules under mcp/.
# Prompts for GitHub URL, adds submodule, syncs recursively, installs to Cursor, integrates docs/worktrees.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p mcp

if command -v uv >/dev/null 2>&1; then
  exec uv run python scripts/add_mcp_submodule.py
else
  exec python3 scripts/add_mcp_submodule.py
fi
