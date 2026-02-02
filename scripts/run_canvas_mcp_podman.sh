#!/usr/bin/env bash
# Build and run the Canvas LMS MCP server in a Podman container.
#
# Uses the main project Dockerfile. The container runs the MCP server in
# streamable-http mode on port 8000 so you can connect with MCP Inspector
# or other HTTP MCP clients.
#
# Requires: Podman, .env with CANVAS_API_TOKEN and CANVAS_BASE_URL (or pass via env).
# Run from repo root.
#
# Usage:
#   ./scripts/run_canvas_mcp_podman.sh
#   CANVAS_API_TOKEN=xxx CANVAS_BASE_URL=https://... ./scripts/run_canvas_mcp_podman.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

IMAGE_NAME="${IMAGE_NAME:-canvas-lms-mcp:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-canvas-mcp-server}"
PORT="${PORT:-8000}"

# Load .env if present (do not override existing env)
if [ -f .env ]; then
  set -a
  # shellcheck source=/dev/null
  source .env
  set +a
fi

echo "Building image $IMAGE_NAME from Dockerfile..."
podman build -f Dockerfile -t "$IMAGE_NAME" .

podman rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo "Running Canvas MCP server (streamable-http) on port $PORT..."
podman run -d --name "$CONTAINER_NAME" \
  -p "${PORT}:8000" \
  -e CANVAS_API_TOKEN="${CANVAS_API_TOKEN:-}" \
  -e CANVAS_BASE_URL="${CANVAS_BASE_URL:-https://texastech.instructure.com}" \
  "$IMAGE_NAME" \
  http

echo "Canvas MCP server is available at http://localhost:$PORT (streamable-http)."
echo "Test with: npx @modelcontextprotocol/inspector (then connect to the URL)."
echo "Stop with: podman stop $CONTAINER_NAME"
