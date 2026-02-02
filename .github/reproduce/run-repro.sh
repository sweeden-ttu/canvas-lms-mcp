#!/usr/bin/env bash
# Build one Podman image and run one Podman pod (single container) to reproduce
# the CI build-test steps. Writes repro.log and extracts error lines to repro-errors.txt.
# Run from repo root on a self-hosted runner with Podman installed.
# One pod per CI/CD job only.

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"
IMAGE_NAME="${IMAGE_NAME:-canvas-lms-mcp-repro}"
POD_NAME="${POD_NAME:-repro-pod}"
LOG_FILE="${LOG_FILE:-repro.log}"
ERRORS_FILE="${ERRORS_FILE:-repro-errors.txt}"

: > "$LOG_FILE"

# Remove any existing pod with this name (idempotent)
podman pod rm -f "$POD_NAME" 2>/dev/null || true
podman rmi -f "$IMAGE_NAME" 2>/dev/null || true

echo "Building Podman image $IMAGE_NAME..."
podman build -f .github/reproduce/Dockerfile.repro -t "$IMAGE_NAME" . 2>&1 | tee -a "$LOG_FILE" || true

echo "Creating one pod $POD_NAME..."
podman pod create --name "$POD_NAME" 2>&1 | tee -a "$LOG_FILE" || true

echo "Running reproduction (one container in pod)..."
podman run --rm --pod "$POD_NAME" \
    -e CANVAS_API_TOKEN="${CANVAS_API_TOKEN:-}" \
    -e CANVAS_BASE_URL="${CANVAS_BASE_URL:-}" \
    "$IMAGE_NAME" 2>&1 | tee -a "$LOG_FILE" || true

# Review log for errors: common failure patterns
echo "Reviewing log for errors..."
grep -E -i '(FAILED|Error|error:|ERROR|Traceback|AssertionError|SyntaxError|ImportError)' "$LOG_FILE" > "$ERRORS_FILE" 2>/dev/null || true
if [ -s "$ERRORS_FILE" ]; then
  echo "Error lines written to $ERRORS_FILE"
  cat "$ERRORS_FILE"
fi

# Teardown: one pod per job, remove it when done
podman pod rm -f "$POD_NAME" 2>/dev/null || true

echo "Reproduction complete. Log: $LOG_FILE"
