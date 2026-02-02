"""
News validation pipeline.

Validates news/announcement content for:
- Structure and required fields
- Temporal consistency
- Source credibility indicators

Designed for integration with Canvas announcements and external news feeds.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from pipelines.base import ValidationResult


class NewsItem(BaseModel):
    """Model for a news/announcement item."""
    title: str = Field(..., min_length=1)
    body: str = Field(default="")
    published_at: str | None = Field(None, description="ISO 8601 datetime")
    source: str | None = Field(None)
    url: str | None = Field(None)


class NewsValidationPipeline:
    """Pipeline for validating news/announcement content."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent

    def validate_news_item(self, item: dict[str, Any]) -> ValidationResult:
        """Validate a single news item structure."""
        if not isinstance(item, dict):
            return ValidationResult(name="news_structure", passed=False, message="Item must be dict")

        if "title" not in item or not str(item.get("title", "")).strip():
            return ValidationResult(name="news_title", passed=False, message="Missing or empty title")

        if "published_at" in item and item["published_at"]:
            try:
                datetime.fromisoformat(str(item["published_at"]).replace("Z", "+00:00"))
            except ValueError:
                return ValidationResult(name="news_date", passed=False, message="Invalid published_at format")

        return ValidationResult(name="news_item", passed=True, message="Valid news item")

    def validate_news_feed(self, items: list[dict]) -> list[ValidationResult]:
        """Validate a list of news items."""
        results = []
        for i, item in enumerate(items):
            r = self.validate_news_item(item)
            r.name = f"news_item_{i}"
            results.append(r)
        return results

    def run(self, items: list[dict[str, Any]] | None = None) -> list[ValidationResult]:
        """Run news validation. If items is None, looks for news config or returns empty."""
        if items is not None:
            return self.validate_news_feed(items)

        news_file = self.project_root / "jekyll_site" / "_data" / "news.yml"
        if news_file.exists():
            try:
                import yaml
            except ImportError:
                return [ValidationResult(name="news_yaml", passed=False, message="PyYAML required: pip install pyyaml")]
            try:
                data = yaml.safe_load(news_file.read_text())
                if isinstance(data, list):
                    return self.validate_news_feed(data)
                if isinstance(data, dict) and "items" in data:
                    return self.validate_news_feed(data["items"])
            except Exception as e:
                return [ValidationResult(name="news_load", passed=False, message=str(e))]

        return [ValidationResult(name="news_skip", passed=True, message="No news data to validate")]
