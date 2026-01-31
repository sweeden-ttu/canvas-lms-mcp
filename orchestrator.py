#!/usr/bin/env python3
"""
Canvas Adaptive Learning Pipeline Orchestrator

Coordinates: Canvas fetch -> course content extraction -> blog series generation
            -> Trustworthy AI peer review Reveal.js presentation.

Uses CANVAS_API_TOKEN from environment (.env).

Usage:
    uv run python orchestrator.py --course-id 58606
    uv run python orchestrator.py --course-id 58606 --output-dir ./output
    uv run python orchestrator.py --course-id 58606 --article "My Trustworthy AI Paper"
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from adaptive_learner.learner import AdaptiveCourseLearner
from content_pipeline.blog_generator import course_content_to_blog_series
from content_pipeline.reveal_generator import generate_trustworthy_ai_review_deck


def run_pipeline(
    course_id: int,
    output_dir: Path,
    article_title: str = "Trustworthy AI Scientific Article",
    iterations: int = 5,
) -> dict:
    """
    Run full pipeline: fetch -> learn -> blog -> reveal.

    Returns:
        dict with keys: course_content, blog_files, reveal_path, context
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    posts_dir = output_dir / "_posts"
    slides_dir = output_dir / "slides"

    # 1. Fetch and learn from course
    learner = AdaptiveCourseLearner(knowledge_base_path=output_dir / "knowledge_base")
    course_content = learner.get_course_content(course_id)
    context = learner.learn_from_course(course_id, iterations=iterations)

    # 2. Generate blog series
    series_slug = f"course-{course_id}-notes"
    blog_files = course_content_to_blog_series(
        course_content,
        output_dir=posts_dir,
        series_slug=series_slug,
        series_title=f"Course {course_id} Notes",
    )

    # 3. Extract summary bullets from context for Reveal deck
    summary_bullets = [
        f"Course {course_id}: {len(course_content.get('modules', []))} modules",
        f"Total items: {sum(len(m.get('items', [])) for m in course_content.get('modules', []))}",
        "Content extracted via adaptive learner (perceptron + RL)",
        "Peer review structure: Trustworthy AI pillars (fairness, privacy, robustness, etc.)",
        "Presentation follows CS Masters-level review workflow",
    ]

    # 4. Generate Trustworthy AI peer review Reveal.js deck
    reveal_path = slides_dir / "trustworthy-ai-peer-review.html"
    generate_trustworthy_ai_review_deck(
        article_title=article_title,
        summary_bullets=summary_bullets,
        output_path=reveal_path,
    )

    return {
        "course_content": course_content,
        "blog_files": [str(p) for p in blog_files],
        "reveal_path": str(reveal_path),
        "context": context,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canvas Adaptive Learning Pipeline Orchestrator"
    )
    parser.add_argument(
        "--course-id",
        type=int,
        required=True,
        help="Canvas course ID to fetch",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output"),
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--article",
        type=str,
        default="Trustworthy AI Scientific Article",
        help="Title of article for peer review presentation",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="RL iterations for context building (default: 5)",
    )
    args = parser.parse_args()

    try:
        result = run_pipeline(
            course_id=args.course_id,
            output_dir=args.output_dir,
            article_title=args.article,
            iterations=args.iterations,
        )
        print("Pipeline completed successfully.")
        print(f"  Blog posts: {len(result['blog_files'])}")
        print(f"  Reveal deck: {result['reveal_path']}")
        print(f"  Context items: {len(result['context'])}")
        return 0
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
