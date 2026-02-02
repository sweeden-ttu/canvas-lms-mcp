#!/usr/bin/env python3
"""
Ingest one MCP submodule (mcp/<name>), optionally embed, and create expert prompt template.

Creates .cursor/prompts/mcp-<name>.md and appends to embedding index for that server.
Use real tool schemas and README only (no synthetic data). See
docs/EMBEDDINGS_AND_PROMPTS_PLAN.md and scripts/add_mcp_submodule.py.

Run: uv run python scripts/embed_mcp_server.py <server-name> [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_DIR = REPO_ROOT / "mcp"
CURSOR_PROMPTS = REPO_ROOT / ".cursor" / "prompts"

PROMPT_TEMPLATE = """# Expert MCP integration: {server_name}

Use the following context for the **{server_name}** MCP server. Prefer real API calls and real data; do not use mock or dummy data.

## Retrieved context

[Retrieved context for {server_name} — fill from embedding index at query time]

## Evaluation areas

When using this server, evaluate usefulness for:

1. **Canvas content**: Retrieving files from Canvas; reviewing and indexing course content.
2. **Documentation and examples**: Crawling docs and examples that enhance skills/agents.
3. **Presentations and orchestration**: Enhancing Reveal.js presentation or BayesianOrchestrator.
4. **Cross-MCP and schema**: Combining with other MCP servers; schema and template updates.

## Checklist (per server)

- [ ] Embeddings generated for README and tools (no synthetic payloads).
- [ ] Step 7 (evaluate MCP command usefulness) run for the four areas above.
- [ ] review-changes step run: reproduce ingestion/embed, peer review, accept or reject premise.
"""


def ensure_prompts_dir() -> Path:
    CURSOR_PROMPTS.mkdir(parents=True, exist_ok=True)
    return CURSOR_PROMPTS


def get_mcp_sources(server_name: str) -> list[Path]:
    """Paths under mcp/<name>/ to ingest (README, docs, etc.)."""
    base = MCP_DIR / server_name
    if not base.is_dir():
        return []
    sources: list[Path] = []
    for name in ["README.md", "README.rst"]:
        p = base / name
        if p.is_file():
            sources.append(p)
    docs = base / "docs"
    if docs.is_dir():
        for p in docs.rglob("*.md"):
            sources.append(p)
    return sources


def write_prompt_template(server_name: str, dry_run: bool) -> bool:
    """Write .cursor/prompts/mcp-<name>.md."""
    ensure_prompts_dir()
    path = CURSOR_PROMPTS / f"mcp-{server_name}.md"
    content = PROMPT_TEMPLATE.format(server_name=server_name)
    if dry_run:
        print(f"Would write {path} ({len(content)} chars)")
        return True
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed one MCP submodule and create expert prompt")
    parser.add_argument("server_name", help="MCP server name (directory under mcp/)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files")
    args = parser.parse_args()
    server_name = args.server_name.strip()
    if not server_name:
        print("error: server_name required", file=sys.stderr)
        return 1
    sources = get_mcp_sources(server_name)
    print(f"embed_mcp_server: {server_name} — {len(sources)} source files")
    write_prompt_template(server_name, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
