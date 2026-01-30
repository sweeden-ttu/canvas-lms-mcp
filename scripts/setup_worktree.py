#!/usr/bin/env python3
"""
Setup worktree: discover and report all Cursor skills and agents in this repository.
Uses UV for Python; run via: uv run python scripts/setup_worktree.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def repo_root() -> Path:
    """Project root (directory containing pyproject.toml or .cursor)."""
    cwd = Path.cwd()
    for d in [cwd, *cwd.parents]:
        if (d / "pyproject.toml").exists() or (d / ".cursor").is_dir():
            return d
    return cwd


def discover_skills(root: Path) -> list[dict]:
    """Discover .cursor/skills/*/SKILL.md and parse frontmatter name/description."""
    skills_dir = root / ".cursor" / "skills"
    if not skills_dir.is_dir():
        return []
    out = []
    for path in sorted(skills_dir.iterdir()):
        if not path.is_dir():
            continue
        skill_md = path / "SKILL.md"
        if not skill_md.is_file():
            continue
        meta = _parse_frontmatter(skill_md.read_text())
        out.append({
            "name": meta.get("name", path.name),
            "description": meta.get("description", ""),
            "path": str(skill_md.relative_to(root)),
        })
    return out


def discover_cursor_agents(root: Path) -> list[dict]:
    """Discover .cursor/agents/*.md and parse frontmatter."""
    agents_dir = root / ".cursor" / "agents"
    if not agents_dir.is_dir():
        return []
    out = []
    for path in sorted(agents_dir.glob("*.md")):
        meta = _parse_frontmatter(path.read_text())
        out.append({
            "name": meta.get("name", path.stem),
            "description": meta.get("description", ""),
            "path": str(path.relative_to(root)),
        })
    return out


def discover_python_agents(root: Path) -> list[dict]:
    """Discover agents/*.py (e.g. agents/bayesian/) as Python agents."""
    agents_base = root / "agents"
    if not agents_base.is_dir():
        return []
    out = []
    for path in sorted(agents_base.rglob("*.py")):
        if path.name.startswith("_"):
            continue
        # Heuristic: module path and docstring first line as description
        rel = path.relative_to(root)
        module = str(rel.with_suffix("")).replace(os.sep, ".")
        desc = _first_docstring_line(path.read_text())
        out.append({
            "name": path.stem,
            "module": module,
            "description": desc or "(Python agent)",
            "path": str(rel),
        })
    return out


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter (name, description) from markdown."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    data = {}
    for line in block.splitlines():
        m = re.match(r"^(\w+):\s*(.+)$", line.strip())
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1].replace('\\"', '"')
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1].replace("\\'", "'")
            data[key] = value
    return data


def _first_docstring_line(text: str) -> str:
    """First line of module docstring."""
    match = re.search(r'"""\s*(.+?)(?:\n|""")', text, re.DOTALL)
    if match:
        return match.group(1).strip().split("\n")[0].strip()
    return ""


def ensure_env_from_example(root: Path) -> str:
    """If .env missing, copy .env.example to .env. Return 'exists' | 'created' | 'missing'."""
    env = root / ".env"
    example = root / ".env.example"
    if env.exists():
        return "exists"
    if example.exists():
        env.write_text(example.read_text())
        return "created"
    return "missing"


def main() -> int:
    root = repo_root()
    os.chdir(root)

    skills = discover_skills(root)
    cursor_agents = discover_cursor_agents(root)
    python_agents = discover_python_agents(root)

    env_status = ensure_env_from_example(root)
    if env_status == "created":
        print("Created .env from .env.example; fill in secrets.")
    elif env_status == "missing":
        print("No .env or .env.example found; create .env if this project needs it.")

    print("=== Skills (.cursor/skills) ===")
    for s in skills:
        desc = s.get("description", "")
        short = (desc[:70] + "...") if len(desc) > 70 else desc
        print(f"  - {s['name']}: {short}")
        print(f"    path: {s['path']}")
    if not skills:
        print("  (none)")

    print("\n=== Cursor agents (.cursor/agents) ===")
    for a in cursor_agents:
        desc = a.get("description", "")
        short = (desc[:70] + "...") if len(desc) > 70 else desc
        print(f"  - {a['name']}: {short}")
        print(f"    path: {a['path']}")
    if not cursor_agents:
        print("  (none)")

    print("\n=== Python agents (agents/) ===")
    for a in python_agents:
        desc = a.get("description", "")
        short = (desc[:70] + "...") if len(desc) > 70 else desc
        print(f"  - {a['name']} ({a.get('module', '')}): {short}")
        print(f"    path: {a['path']}")
    if not python_agents:
        print("  (none)")

    print("\n=== Summary ===")
    print(f"  Skills: {len(skills)}  |  Cursor agents: {len(cursor_agents)}  |  Python agents: {len(python_agents)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
