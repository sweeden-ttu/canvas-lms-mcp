#!/usr/bin/env python3
"""Generate status badges for the Canvas LMS MCP repository.

This script generates JSON endpoint files for dynamic shields.io badges
and provides markdown snippets for use in README files.

Usage:
    python scripts/generate_badges.py [--output-dir .github/badges]
"""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class Badge:
    """Represents a status badge."""
    
    label: str
    message: str
    color: str
    logo: str = ""
    logo_color: str = "white"
    
    def to_shields_url(self) -> str:
        """Generate shields.io URL."""
        # URL encode spaces and special characters
        label = self.label.replace(" ", "%20").replace("-", "--")
        message = self.message.replace(" ", "%20").replace("-", "--")
        
        url = f"https://img.shields.io/badge/{label}-{message}-{self.color}"
        
        params = []
        if self.logo:
            params.append(f"logo={self.logo}")
        if self.logo_color and self.logo:
            params.append(f"logoColor={self.logo_color}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    def to_markdown(self, link: str = "") -> str:
        """Generate markdown image, optionally with link."""
        img = f"![{self.label}]({self.to_shields_url()})"
        if link:
            return f"[{img}]({link})"
        return img
    
    def to_json(self) -> dict:
        """Generate endpoint JSON for dynamic badges."""
        return {
            "schemaVersion": 1,
            "label": self.label,
            "message": self.message,
            "color": self.color,
        }
    
    def to_html(self) -> str:
        """Generate HTML img tag."""
        return f'<img src="{self.to_shields_url()}" alt="{self.label}">'


# Predefined badges for the project
PROJECT_BADGES = [
    # Build and CI
    Badge("build", "passing", "brightgreen", "github"),
    Badge("tests", "passing", "brightgreen", "pytest"),
    
    # Integrations
    Badge("AutoGen", "enabled", "purple", "microsoft"),
    Badge("LangSmith", "enabled", "00A67E", "langchain"),
    Badge("MCP", "active", "blue"),
    
    # Sync status
    Badge("GitLab", "synced", "fc6d26", "gitlab"),
    Badge("GitHub", "synced", "181717", "github"),
    
    # Technology
    Badge("Python", "3.10+", "3776AB", "python"),
    Badge("FastMCP", "1.2+", "green"),
    
    # Quality
    Badge("code style", "ruff", "D7FF64", "ruff"),
    Badge("type checked", "mypy", "blue"),
]


def generate_badge_files(output_dir: Path) -> list[str]:
    """Generate badge JSON files and return markdown lines."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    markdown_lines = []
    
    for badge in PROJECT_BADGES:
        # Generate JSON endpoint file
        filename = badge.label.lower().replace(" ", "-") + ".json"
        json_path = output_dir / filename
        json_path.write_text(json.dumps(badge.to_json(), indent=2))
        
        # Collect markdown
        markdown_lines.append(badge.to_markdown())
    
    return markdown_lines


def generate_readme_badges() -> str:
    """Generate badge markdown section for README."""
    lines = [
        "## Status Badges",
        "",
        "### Build Status",
        "[![Build](https://img.shields.io/github/actions/workflow/status/sweeden-ttu/canvas-lms-mcp/autogen-ci.yml?label=AutoGen%20CI&logo=github)](https://github.com/sweeden-ttu/canvas-lms-mcp/actions/workflows/autogen-ci.yml)",
        "[![LangSmith CI](https://img.shields.io/github/actions/workflow/status/sweeden-ttu/canvas-lms-mcp/langsmith-ci.yml?label=LangSmith%20CI&logo=github)](https://github.com/sweeden-ttu/canvas-lms-mcp/actions/workflows/langsmith-ci.yml)",
        "",
        "### Integrations",
        "[![AutoGen](https://img.shields.io/badge/AutoGen-Enabled-purple?logo=microsoft)](https://microsoft.github.io/autogen/)",
        "[![LangSmith](https://img.shields.io/badge/LangSmith-Enabled-00A67E?logo=langchain)](https://smith.langchain.com/)",
        "[![MCP](https://img.shields.io/badge/MCP-Active-blue)](https://modelcontextprotocol.io/)",
        "",
        "### Repository Sync",
        "[![GitLab Sync](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab)](https://gitlab.com/sweeden-ttu/canvas-lms-mcp)",
        "",
        "### Technology",
        "[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)",
        "[![Code Style](https://img.shields.io/badge/code%20style-ruff-D7FF64?logo=ruff)](https://docs.astral.sh/ruff/)",
    ]
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate status badges")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".github/badges"),
        help="Output directory for badge JSON files",
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        help="Print README badge markdown",
    )
    args = parser.parse_args()
    
    if args.readme:
        print(generate_readme_badges())
        return
    
    # Generate badge files
    markdown_lines = generate_badge_files(args.output_dir)
    
    print(f"Generated {len(PROJECT_BADGES)} badge files in {args.output_dir}")
    print()
    print("Badge Markdown (inline):")
    print(" ".join(markdown_lines[:5]))  # First 5 badges
    print()
    print("Run with --readme for full README section")


if __name__ == "__main__":
    main()
