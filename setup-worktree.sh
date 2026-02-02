#!/usr/bin/env bash
# setup-worktree: UV-based setup that utilizes all skills and agents in this repository.
# Run from repo root: ./setup-worktree.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# --- Step 1: Ensure UV is available ---
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "[setup-worktree] Using uv: $(uv --version)"

# --- Step 2: Sync dependencies (UV Python) ---
echo "[setup-worktree] Syncing dependencies (uv sync --all-extras --dev)..."
uv sync --all-extras --dev

# --- Step 3: Optional .env from .env.example (handled by Python script) ---
if [[ ! -f .env ]] && [[ -f .env.example ]]; then
  cp .env.example .env
  echo "[setup-worktree] Created .env from .env.example; fill in CANVAS_API_TOKEN and CANVAS_BASE_URL."
fi

# --- Step 4: Discover and report all skills and agents ---
echo "[setup-worktree] Discovering skills and agents..."
uv run python scripts/setup_worktree.py

# --- Step 5: Quick validation (optional) ---
echo "[setup-worktree] Running quick checks..."
uv run python -c "
from pathlib import Path
root = Path('.')
# Ensure .cursor structure
cursor = root / '.cursor'
skills = cursor / 'skills'
agents = cursor / 'agents'
assert cursor.is_dir(), '.cursor/ not found'
assert skills.is_dir(), '.cursor/skills/ not found'
assert agents.is_dir(), '.cursor/agents/ not found'
print('  .cursor/skills and .cursor/agents OK')
# Ensure agents/bayesian if referenced
bayesian = root / 'agents' / 'bayesian'
if bayesian.is_dir():
    print('  agents/bayesian OK')
print('  Checks passed.')
"

echo "[setup-worktree] Done. Skills and agents are available to Cursor in this worktree."
