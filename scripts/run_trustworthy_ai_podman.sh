#!/usr/bin/env bash
# Build and run the Trustworthy AI container with Podman.
# Uses gitlab.com/sweeden3/trustworthy-ai. Run from canvas-lms-mcp repo root.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

IMAGE_NAME="${IMAGE_NAME:-trustworthy-ai:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-trustworthy-ai}"
PORT="${PORT:-8080}"

echo "Building image $IMAGE_NAME from containers/trustworthy-ai/Containerfile..."
podman build -f containers/trustworthy-ai/Containerfile -t "$IMAGE_NAME" .

podman rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo "Running container $CONTAINER_NAME on port $PORT..."
podman run -d --name "$CONTAINER_NAME" -p "${PORT}:80" "$IMAGE_NAME"

echo "Trustworthy AI is available at http://localhost:$PORT"
echo "Stop with: podman stop $CONTAINER_NAME"
