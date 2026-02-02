#!/usr/bin/env python3
"""
Run all validation pipelines: content, link, news.

Optionally integrates with LangSmith for tracing when LANGCHAIN_API_KEY is set.

Usage:
    uv run python pipelines/run_pipelines.py
"""

import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.content_validator import ContentValidationPipeline
from pipelines.link_validator import LinkValidationPipeline
from pipelines.news_validator import NewsValidationPipeline


def main() -> int:
    root = Path(__file__).parent.parent

    # Content validation
    print("=== Content Validation ===")
    cv = ContentValidationPipeline(root)
    for r in cv.run():
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.message}")

    # Link validation (limited to avoid network spam)
    print("\n=== Link Validation (jekyll_site only) ===")
    lv = LinkValidationPipeline(root)
    results = []
    jekyll = root / "jekyll_site"
    if jekyll.exists():
        for p in jekyll.rglob("*.md"):
            results.extend(lv.validate_file(p))
    for r in results[:10]:  # Limit output
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.message}")
    if len(results) > 10:
        print(f"  ... and {len(results) - 10} more")

    # News validation
    print("\n=== News Validation ===")
    nv = NewsValidationPipeline(root)
    for r in nv.run():
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.message}")

    content_results = cv.run()
    news_results = nv.run()
    all_passed = all(r.passed for r in content_results) and all(r.passed for r in news_results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
