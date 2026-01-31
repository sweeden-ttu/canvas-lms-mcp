"""
Unit tests for the pipeline orchestrator.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


SAMPLE_COURSE = {
    "course_id": 58606,
    "modules": [
        {"id": 1, "name": "Module 1", "items": [{"title": "Item 1", "type": "Page"}]},
        {"id": 2, "name": "Module 2", "items": []},
    ],
}


class TestOrchestrator:
    """Tests for run_pipeline."""

    def test_run_pipeline_produces_output(self, tmp_path):
        from orchestrator import run_pipeline

        with patch("orchestrator.AdaptiveCourseLearner") as mock_learner_cls:
            mock_learner = MagicMock()
            mock_learner.get_course_content.return_value = SAMPLE_COURSE
            mock_learner.learn_from_course.return_value = [
                "Module 1: Item 1",
                "Module 2: ",
            ]
            mock_learner_cls.return_value = mock_learner

            result = run_pipeline(
                course_id=58606,
                output_dir=tmp_path,
                article_title="Test Article",
                iterations=2,
            )

            assert "blog_files" in result
            assert "reveal_path" in result
            assert "context" in result
            assert len(result["blog_files"]) == 2
            assert result["reveal_path"].endswith(".html")
            assert Path(result["reveal_path"]).exists()

    def test_run_pipeline_creates_directories(self, tmp_path):
        from orchestrator import run_pipeline

        with patch("orchestrator.AdaptiveCourseLearner") as mock_learner_cls:
            mock_learner = MagicMock()
            mock_learner.get_course_content.return_value = SAMPLE_COURSE
            mock_learner.learn_from_course.return_value = []
            mock_learner_cls.return_value = mock_learner

            run_pipeline(course_id=58606, output_dir=tmp_path)

            assert (tmp_path / "_posts").exists()
            assert (tmp_path / "slides").exists()
