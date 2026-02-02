#!/usr/bin/env python3
"""
Embed project docs, skills, agents, and rules for deep-dive and RAG.

Ingests docs/, .cursor/skills/, .cursor/agents/, README, CLAUDE.md, worktrees.json,
.cursor/rules; chunks content; optionally generates embeddings and writes index to
.cursor/embeddings/. Use real content only (no synthetic data). See
docs/EMBEDDINGS_AND_PROMPTS_PLAN.md.

Run: uv run python scripts/embed_docs.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CURSOR_EMBED = REPO_ROOT / ".cursor" / "embeddings"
CURSOR_PROMPTS = REPO_ROOT / ".cursor" / "prompts"


def repo_root() -> Path:
    """Project root (pyproject.toml or .cursor)."""
    cwd = Path.cwd()
    for d in [cwd, *cwd.parents]:
        if (d / "pyproject.toml").exists() or (d / ".cursor").is_dir():
            return d
    return REPO_ROOT


def ensure_dirs(root: Path) -> None:
    """Create .cursor/embeddings and .cursor/prompts if missing."""
    (root / ".cursor" / "embeddings").mkdir(parents=True, exist_ok=True)
    (root / ".cursor" / "prompts").mkdir(parents=True, exist_ok=True)


def collect_sources(root: Path) -> list[tuple[str, Path]]:
    """Collect paths to embed: docs, skills, agents, key files."""
    sources: list[tuple[str, Path]] = []
    # Project docs
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for p in sorted(docs_dir.glob("*.md")):
            sources.append(("doc", p))
    for name in ["README.md", "CLAUDE.md", "DOCKER.md"]:
        p = root / name
        if p.is_file():
            sources.append(("doc", p))
    # Cursor skills
    skills_dir = root / ".cursor" / "skills"
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir():
                sk = d / "SKILL.md"
                if sk.is_file():
                    sources.append(("skill", sk))
    # Cursor agents
    agents_dir = root / ".cursor" / "agents"
    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.md")):
            sources.append(("agent", p))
    # Rules and worktrees
    rules_dir = root / ".cursor" / "rules"
    if rules_dir.is_dir():
        for p in sorted(rules_dir.glob("*.mdc")):
            sources.append(("rule", p))
    wt = root / ".cursor" / "worktrees.json"
    if wt.is_file():
        sources.append(("worktree", wt))
    return sources


def run_ingest(root: Path, dry_run: bool) -> dict:
    """Ingest sources and write minimal index/meta (Phase 1 placeholder)."""
    ensure_dirs(root)
    sources = collect_sources(root)
    meta: list[dict] = []
    for typ, path in sources:
        rel = path.relative_to(root)
        meta.append({
            "source": str(rel),
            "type": typ,
            "path": str(path),
        })
    out_index = root / ".cursor" / "embeddings" / "index.json"
    out_meta = root / ".cursor" / "embeddings" / "meta.json"
    if not dry_run:
        out_index.write_text(json.dumps({"chunks": [], "version": "0.1.0"}, indent=2))
        out_meta.write_text(json.dumps({"sources": meta, "version": "0.1.0"}, indent=2))
    return {"sources": len(sources), "meta_entries": len(meta), "dry_run": dry_run}


def main() -> int:
    parser = argparse.ArgumentParser(description="Embed project docs for deep-dive/RAG")
    parser.add_argument("--dry-run", action="store_true", help="Only list sources, do not write")
    args = parser.parse_args()
    root = repo_root()
    result = run_ingest(root, args.dry_run)
    print(f"embed_docs: {result['sources']} sources, {result['meta_entries']} meta entries (dry_run={result['dry_run']})")
    if not args.dry_run:
        print("Wrote .cursor/embeddings/index.json and meta.json (placeholder). Full embedding in Phase 1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
