"""Tests for validation pipelines."""

import pytest
from pathlib import Path

from pipelines.base import ValidationResult
from pipelines.content_validator import ContentValidationPipeline
from pipelines.news_validator import NewsValidationPipeline, NewsItem


class TestContentValidationPipeline:
    """Tests for content validation."""

    def test_validate_manifest_exists(self):
        cv = ContentValidationPipeline(Path(__file__).parent.parent)
        r = cv.validate_manifest(Path("course_content/CS5374-Spring2026/manifest.json"))
        assert r.passed
        assert "7 modules" in r.message

    def test_validate_manifest_missing(self):
        cv = ContentValidationPipeline(Path(__file__).parent.parent)
        r = cv.validate_manifest(Path("nonexistent/manifest.json"))
        assert not r.passed
        assert "not found" in r.message

    def test_validate_jekyll_front_matter_valid(self):
        cv = ContentValidationPipeline()
        content = "---\nlayout: page\ntitle: Test\n---\n\nBody"
        r = cv.validate_jekyll_front_matter(content)
        assert r.passed

    def test_validate_jekyll_front_matter_invalid(self):
        cv = ContentValidationPipeline()
        r = cv.validate_jekyll_front_matter("No front matter here")
        assert not r.passed


class TestNewsValidationPipeline:
    """Tests for news validation."""

    def test_validate_news_item_valid(self):
        nv = NewsValidationPipeline()
        r = nv.validate_news_item({"title": "Test", "body": "Content"})
        assert r.passed

    def test_validate_news_item_missing_title(self):
        nv = NewsValidationPipeline()
        r = nv.validate_news_item({"body": "Content"})
        assert not r.passed

    def test_validate_news_item_invalid_date(self):
        nv = NewsValidationPipeline()
        r = nv.validate_news_item({"title": "Test", "published_at": "not-a-date"})
        assert not r.passed
