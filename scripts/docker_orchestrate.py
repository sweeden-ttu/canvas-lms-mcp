#!/usr/bin/env python3
"""
Docker orchestration: two worktrees (Canvas LMS content + Trustworthy AI presentation).

- Worktree 1: Canvas LMS content retrieval - skeleton/ToC from course syllabus, fill with subagents.
- Worktree 2: Trustworthy AI presentation-generator - skeleton/ToC from topic, fill with subagents.
- CI/CD plan: Mermaid + Markdown; hypothesis_generator; cross-repo evidence_evaluator;
  read CI/CD and Docker logs and fix errors; align Dockerfile with GitHub/GitLab workflows;
  update schema files, skeleton, and ToC for presentation-generator and BayesianOrchestrator.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    cwd = Path.cwd()
    for d in [cwd, *cwd.parents]:
        if (d / "pyproject.toml").exists() or (d / "server.py").exists():
            return d
    return cwd


def ensure_worktrees(worktree_canvas: Path, worktree_trustworthy_ai: Path) -> None:
    worktree_canvas.mkdir(parents=True, exist_ok=True)
    worktree_trustworthy_ai.mkdir(parents=True, exist_ok=True)
    (worktree_canvas / "skeleton").mkdir(parents=True, exist_ok=True)
    (worktree_canvas / "toc").mkdir(parents=True, exist_ok=True)
    (worktree_trustworthy_ai / "skeleton").mkdir(parents=True, exist_ok=True)
    (worktree_trustworthy_ai / "toc").mkdir(parents=True, exist_ok=True)


def write_canvas_skeleton_and_toc(worktree_canvas: Path) -> None:
    """Build skeleton and ToC for Canvas LMS content retrieval from course syllabus."""
    toc = {
        "title": "Canvas LMS Content Retrieval",
        "source": "course syllabus",
        "sections": [
            {"id": "s1", "title": "Course overview", "subsections": []},
            {"id": "s2", "title": "Modules and assignments", "subsections": []},
            {"id": "s3", "title": "Announcements and discussions", "subsections": []},
            {"id": "s4", "title": "Grades and calendar", "subsections": []},
        ],
    }
    (worktree_canvas / "toc" / "toc.json").write_text(json.dumps(toc, indent=2))
    (worktree_canvas / "skeleton" / "README.md").write_text(
        "# Canvas LMS Content Retrieval\n\n"
        "Skeleton built from course syllabus. Fill sections using Canvas MCP and subagents.\n"
    )


def write_trustworthy_ai_skeleton_and_toc(worktree_trustworthy_ai: Path) -> None:
    """Build skeleton and ToC for Trustworthy AI presentation (presentation-generator)."""
    toc = {
        "title": "Trustworthy AI",
        "source": "presentation topic",
        "sections": [
            {"id": "s1", "title": "Title and introduction", "subsections": []},
            {"id": "s2", "title": "Fairness", "subsections": []},
            {"id": "s3", "title": "Privacy and security", "subsections": []},
            {"id": "s4", "title": "Robustness and transparency", "subsections": []},
            {"id": "s5", "title": "Governance and conclusion", "subsections": []},
        ],
    }
    (worktree_trustworthy_ai / "toc" / "toc.json").write_text(json.dumps(toc, indent=2))
    (worktree_trustworthy_ai / "skeleton" / "README.md").write_text(
        "# Trustworthy AI Presentation\n\n"
        "Skeleton for presentation-generator. Fill sections using subagents and Reveal.js.\n"
    )


def run_bayesian_orchestrator(root: Path) -> dict | None:
    """Instantiate BayesianOrchestrator (hypothesis_generator, evidence_evaluator)."""
    try:
        sys.path.insert(0, str(root))
        from agents.bayesian import BayesianOrchestrator, OrchestratorConfig
        config = OrchestratorConfig(auto_create_worktrees=False)
        orch = BayesianOrchestrator(config)
        orch.setup_causal_network(
            variables=[
                {"name": "canvas_content_ready", "description": "Canvas content skeleton filled"},
                {"name": "presentation_ready", "description": "Trustworthy AI presentation filled"},
                {"name": "cicd_passing", "description": "CI/CD pipeline passing"},
            ],
            causal_links=[
                {"cause": "canvas_content_ready", "effect": "cicd_passing", "strength": 0.5},
                {"cause": "presentation_ready", "effect": "cicd_passing", "strength": 0.5},
            ],
        )
        summary = orch.reasoner.get_network_summary() if hasattr(orch.reasoner, "get_network_summary") else {"status": "ok"}
        return summary if isinstance(summary, dict) else {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}


def write_cicd_plan_mermaid(out_dir: Path) -> None:
    """Document CI/CD plan with Mermaid and Markdown (align Dockerfile, GitHub, GitLab)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    mermaid = """flowchart LR
  subgraph Docker
    A[Dockerfile] --> B[uv/Python/Autogen/LangSmith]
    B --> C[Two worktrees]
    C --> D[Orchestrate]
  end
  subgraph GitHub
    E[autogen-ci.yml] --> F[build-test]
    F --> G[gitlab-sync]
    F --> H[autogen-agents]
    F --> I[generate-badges]
  end
  subgraph GitLab
    J[Sync from GitHub] --> K[Same tasks]
  end
  A -.-> E
  D -.-> F
"""
    (out_dir / "cicd-plan.mmd").write_text(mermaid)
    md = """# CI/CD Plan (Dockerfile, GitHub, GitLab)

## Same tasks across environments

| Task | Dockerfile | GitHub Actions | GitLab |
|------|------------|----------------|--------|
| Install uv + deps | `uv pip install` | `uv sync --all-extras --dev` | Sync from GitHub |
| Lint (ruff) | (in image) | `uv run ruff check .` | Same via sync |
| Type check (mypy) | (in image) | `uv run mypy server.py` | Same |
| Tests (pytest) | (in image) | `uv run pytest tests/` | Same |
| Two worktrees | `docker_orchestrate.py` | (optional workflow) | Same |
| Hypothesis/evidence | BayesianOrchestrator | AutoGen agents job | Same |
| Badges | (optional) | generate-badges job | Same |

## Mermaid diagram

See `cicd-plan.mmd` for flowchart. Generate with: `mermaid cicd-plan.mmd -o cicd-plan.svg`

## Log-driven error fixes

1. **CI/CD logs**: Read GitHub Actions / GitLab CI logs; fix failing steps (lint, typecheck, tests).
2. **Docker logs**: `docker build` and `docker run`; fix Dockerfile RUN/COPY and entrypoint errors.
3. **Alignment**: Keep Dockerfile install and test steps in sync with `.github/workflows/autogen-ci.yml` and GitLab pipeline.
"""
    (out_dir / "CICD_PLAN.md").write_text(md)


def write_schema_and_toc_updates(
    root: Path,
    worktree_canvas: Path,
    worktree_trustworthy_ai: Path,
) -> None:
    """Emit schema/skeleton/ToC updates for presentation-generator and BayesianOrchestrator."""
    updates_dir = root / "worktrees" / "orchestrator_updates"
    updates_dir.mkdir(parents=True, exist_ok=True)
    (updates_dir / "presentation-generator-toc.json").write_text(
        json.dumps(
            {
                "source": "trustworthy-ai-presentation",
                "toc_path": str(worktree_trustworthy_ai / "toc" / "toc.json"),
                "skeleton_path": str(worktree_trustworthy_ai / "skeleton"),
            },
            indent=2,
        )
    )
    (updates_dir / "bayesian-orchestrator-schema.json").write_text(
        json.dumps(
            {
                "variables": ["canvas_content_ready", "presentation_ready", "cicd_passing"],
                "causal_links": [
                    {"cause": "canvas_content_ready", "effect": "cicd_passing"},
                    {"cause": "presentation_ready", "effect": "cicd_passing"},
                ],
            },
            indent=2,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Docker orchestration: two worktrees + CI/CD plan")
    parser.add_argument("--worktree-canvas", type=Path, default=Path("/app/worktrees/canvas-lms-content"))
    parser.add_argument("--worktree-trustworthy-ai", type=Path, default=Path("/app/worktrees/trustworthy-ai-presentation"))
    parser.add_argument("--output-dir", type=Path, default=None, help="CI/CD plan output dir (default: worktrees)")
    args = parser.parse_args()

    root = repo_root()
    worktree_canvas = args.worktree_canvas.resolve()
    worktree_trustworthy_ai = args.worktree_trustworthy_ai.resolve()
    out_dir = (args.output_dir or root / "worktrees").resolve()

    ensure_worktrees(worktree_canvas, worktree_trustworthy_ai)
    write_canvas_skeleton_and_toc(worktree_canvas)
    write_trustworthy_ai_skeleton_and_toc(worktree_trustworthy_ai)
    write_cicd_plan_mermaid(out_dir)
    write_schema_and_toc_updates(root, worktree_canvas, worktree_trustworthy_ai)

    summary = run_bayesian_orchestrator(root)
    if summary:
        (out_dir / "bayesian_summary.json").write_text(json.dumps(summary, indent=2))

    print("Orchestration complete.")
    print("  Worktree Canvas LMS content:", worktree_canvas)
    print("  Worktree Trustworthy AI presentation:", worktree_trustworthy_ai)
    print("  CI/CD plan:", out_dir / "CICD_PLAN.md")
    print("  Schema/ToC updates: worktrees/orchestrator_updates/")
    if summary and "error" in summary:
        print("  BayesianOrchestrator:", summary["error"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
