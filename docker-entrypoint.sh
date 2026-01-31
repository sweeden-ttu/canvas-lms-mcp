#!/usr/bin/env bash
# Entrypoint: orchestrate two worktrees (Canvas LMS content + Trustworthy AI presentation)
# or run MCP server. Aligns with GitHub/GitLab workflow tasks.

set -e

WORKTREE_CANVAS="${WORKTREE_CANVAS:-/app/worktrees/canvas-lms-content}"
WORKTREE_TRUSTWORTHY_AI="${WORKTREE_TRUSTWORTHY_AI:-/app/worktrees/trustworthy-ai-presentation}"

case "${1:-orchestrate}" in
  server)
    exec python3 /app/server.py "${@:2}"
    ;;
  http)
    exec python3 /app/server.py --transport streamable-http --port 8000 "${@:2}"
    ;;
  embed)
    if command -v uv >/dev/null 2>&1; then
      cd /app && uv sync --all-extras 2>/dev/null || true
      uv run python3 /app/scripts/embed_docs.py
      for dir in /app/mcp/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        uv run python3 /app/scripts/embed_mcp_server.py "$name" 2>/dev/null || true
      done
    else
      python3 /app/scripts/embed_docs.py
      for dir in /app/mcp/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        python3 /app/scripts/embed_mcp_server.py "$name" 2>/dev/null || true
      done
    fi
    exit 0
    ;;
  orchestrate|"")
    # Run UV-based setup (skills/agents discovery)
    if command -v uv >/dev/null 2>&1; then
      cd /app
      uv sync --all-extras 2>/dev/null || true
      uv run python3 /app/scripts/setup_worktree.py 2>/dev/null || true
    else
      python3 /app/scripts/setup_worktree.py 2>/dev/null || true
    fi
    # Run orchestration: two worktrees, skeleton/ToC, CI/CD plan, hypothesis/evidence, schema/ToC updates
    exec python3 /app/scripts/docker_orchestrate.py \
      --worktree-canvas "$WORKTREE_CANVAS" \
      --worktree-trustworthy-ai "$WORKTREE_TRUSTWORTHY_AI"
    ;;
  *)
    exec "$@"
    ;;
esac
