"""
Unit tests for content pipeline (blog generator, Reveal.js generator).
"""

from pathlib import Path

import pytest


SAMPLE_COURSE_CONTENT = {
    "course_id": 58606,
    "modules": [
        {
            "id": 1,
            "name": "Introduction to Trustworthy AI",
            "items": [
                {"id": 1, "title": "What is Trustworthy AI?", "type": "Page"},
                {"id": 2, "title": "Fairness", "type": "File"},
            ],
        },
        {
            "id": 2,
            "name": "Privacy and Security",
            "items": [
                {"id": 3, "title": "Differential Privacy", "type": "ExternalUrl"},
            ],
        },
    ],
}


class TestBlogGenerator:
    """Tests for course_content_to_blog_series."""

    def test_generates_correct_number_of_posts(self, tmp_path):
        from content_pipeline.blog_generator import course_content_to_blog_series

        files = course_content_to_blog_series(
            SAMPLE_COURSE_CONTENT,
            output_dir=tmp_path,
            series_slug="test-series",
        )
        assert len(files) == 2
        assert all(p.exists() for p in files)

    def test_front_matter_valid(self, tmp_path):
        from content_pipeline.blog_generator import course_content_to_blog_series

        files = course_content_to_blog_series(
            SAMPLE_COURSE_CONTENT,
            output_dir=tmp_path,
            series_slug="test",
        )
        content = files[0].read_text()
        assert "layout: post" in content
        assert "title:" in content
        assert "series: test" in content
        assert "part: 1" in content

    def test_content_includes_module_names(self, tmp_path):
        from content_pipeline.blog_generator import course_content_to_blog_series

        files = course_content_to_blog_series(
            SAMPLE_COURSE_CONTENT,
            output_dir=tmp_path,
        )
        content = files[0].read_text()
        assert "Introduction to Trustworthy AI" in content
        assert "What is Trustworthy AI?" in content


class TestRevealGenerator:
    """Tests for generate_trustworthy_ai_review_deck."""

    def test_generates_html_file(self, tmp_path):
        from content_pipeline.reveal_generator import generate_trustworthy_ai_review_deck

        out = tmp_path / "slides" / "review.html"
        path = generate_trustworthy_ai_review_deck(
            article_title="Test Article",
            summary_bullets=["Point 1", "Point 2"],
            output_path=out,
        )
        assert path.exists()
        content = path.read_text()
        assert "Reveal.initialize" in content
        assert "Test Article" in content
        assert "Point 1" in content

    def test_contains_trustworthy_ai_sections(self, tmp_path):
        from content_pipeline.reveal_generator import generate_trustworthy_ai_review_deck

        out = tmp_path / "deck.html"
        generate_trustworthy_ai_review_deck(
            article_title="AI Paper",
            summary_bullets=["Summary"],
            output_path=out,
        )
        content = out.read_text()
        assert "Trustworthy AI" in content
        assert "Fairness" in content
        assert "Privacy" in content
        assert "mermaid" in content
