"""
Blog Series Generator - Converts course content to Jekyll-ready blog posts.

Follows latex-blog-series-publisher conventions with KaTeX and Mermaid support.
"""

from datetime import datetime
from pathlib import Path


def course_content_to_blog_series(
    course_content: dict,
    output_dir: Path,
    series_slug: str = "course-notes",
    series_title: str | None = None,
) -> list[Path]:
    """
    Convert Canvas course content to a Jekyll blog series.

    Args:
        course_content: Dict from AdaptiveCourseLearner with course_id, modules
        output_dir: Base output directory (e.g., _posts/)
        series_slug: URL slug for the series
        series_title: Human-readable series title

    Returns:
        List of generated file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    course_id = course_content.get("course_id", "unknown")
    title = series_title or f"Course {course_id} Notes"

    generated: list[Path] = []
    modules = course_content.get("modules", [])

    for i, module in enumerate(modules, 1):
        module_name = module.get("name", f"Module {i}")
        items = module.get("items", [])

        content_sections = []
        content_sections.append("## Why this matters\n")
        content_sections.append(
            f"This module covers **{module_name}**. "
            "Below is the extracted structure from the course materials.\n"
        )
        content_sections.append("## Key ideas\n")

        for j, item in enumerate(items, 1):
            item_title = item.get("title", f"Item {j}")
            item_type = item.get("type", "Content")
            content_sections.append(f"- **{item_title}** ({item_type})\n")

        content_sections.append("\n## Summary\n")
        content_sections.append(
            f"This module contains {len(items)} item(s). "
            "Use the course materials in Canvas for full details.\n"
        )

        body = "\n".join(content_sections)

        # Jekyll front matter
        today = datetime.now().strftime("%Y-%m-%d")
        part = i
        prev_url = f"/{series_slug}-part-{part - 1}/" if part > 1 else ""
        next_url = f"/{series_slug}-part-{part + 1}/" if part < len(modules) else ""

        front_matter = f"""---
layout: post
title: "{title} - Part {part}: {module_name}"
date: {today}
tags: [canvas, course-notes, trustworthy-ai]
series: {series_slug}
part: {part}
description: "Extracted content from {module_name}"
---
"""
        if prev_url:
            front_matter += f"\nPrevious: [Part {part - 1}]({prev_url})\n"
        if next_url:
            front_matter += f"Next: [Part {part + 1}]({next_url})\n"
        front_matter += "\n---\n\n"

        filename = f"{today}-{series_slug}-part-{part:02d}.md"
        filepath = output_dir / filename
        filepath.write_text(front_matter + body, encoding="utf-8")
        generated.append(filepath)

    return generated
