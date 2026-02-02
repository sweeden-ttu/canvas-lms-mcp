"""
LangChain and LangSmith integration for validation pipelines.

When LANGCHAIN_API_KEY is set, validation runs are traced to LangSmith.
Adds support for:
- Tracing pipeline execution
- Trustworthy AI prompts and evaluation
- Skills integration

Usage:
    LANGCHAIN_API_KEY=xxx uv run python -c "
    from pipelines.langchain_integration import run_with_tracing
    run_with_tracing()
    "
"""

import os
from pathlib import Path

# Optional LangSmith - only import if available
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    traceable = lambda fn: fn  # no-op decorator


def _run_content_validation(root: Path):
    """Run content validation (wrapped for tracing)."""
    from pipelines.content_validator import ContentValidationPipeline

    cv = ContentValidationPipeline(root)
    return cv.run()


def _run_link_validation(root: Path, limit: int = 5):
    """Run link validation (wrapped for tracing)."""
    from pipelines.link_validator import LinkValidationPipeline

    lv = LinkValidationPipeline(root)
    results = []
    jekyll = root / "jekyll_site"
    if jekyll.exists():
        for p in list(jekyll.rglob("*.md"))[:limit]:
            results.extend(lv.validate_file(p))
    return results


def _run_news_validation(root: Path):
    """Run news validation (wrapped for tracing)."""
    from pipelines.news_validator import NewsValidationPipeline

    nv = NewsValidationPipeline(root)
    return nv.run()


if LANGSMITH_AVAILABLE:

    @traceable(name="content_validation")
    def run_content_with_tracing(root: Path) -> list:
        return _run_content_validation(root)

    @traceable(name="link_validation")
    def run_link_with_tracing(root: Path, limit: int = 5) -> list:
        return _run_link_validation(root, limit)

    @traceable(name="news_validation")
    def run_news_with_tracing(root: Path) -> list:
        return _run_news_validation(root)

    @traceable(name="validation_pipelines")
    def run_with_tracing(root: Path | None = None) -> dict:
        """Run all pipelines with LangSmith tracing."""
        root = root or Path(__file__).parent.parent
        return {
            "content": run_content_with_tracing(root),
            "link": run_link_with_tracing(root),
            "news": run_news_with_tracing(root),
        }
else:

    def run_with_tracing(root: Path | None = None) -> dict:
        """Run all pipelines (no tracing - LangSmith not installed)."""
        root = root or Path(__file__).parent.parent
        return {
            "content": _run_content_validation(root),
            "link": _run_link_validation(root),
            "news": _run_news_validation(root),
        }
