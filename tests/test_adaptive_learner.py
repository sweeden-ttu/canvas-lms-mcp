"""
Unit tests for adaptive course learner components.

Config is mocked in conftest.py so tests run without .env.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.fixture
def mock_config():
    """Provide mock Canvas config."""
    with patch("adaptive_learner.canvas_fetcher.load_env_config") as m:
        cfg = MagicMock()
        cfg.base_url = "https://test.instructure.com"
        cfg.api_token = "test-token"
        m.return_value = cfg
        yield cfg


@pytest.fixture
def sample_course_content():
    """Sample course content for testing."""
    return {
        "course_id": 58606,
        "modules": [
            {
                "id": 1,
                "name": "Introduction",
                "items": [
                    {"id": 1, "title": "Welcome", "type": "Page"},
                    {"id": 2, "title": "Syllabus", "type": "File"},
                ],
            },
            {
                "id": 2,
                "name": "Week 1",
                "items": [
                    {"id": 3, "title": "Lecture 1", "type": "ExternalUrl"},
                ],
            },
        ],
    }


class TestPerceptronFeatureExtractor:
    """Tests for PerceptronFeatureExtractor."""

    def test_extract_features_empty(self):
        from adaptive_learner.perceptron_model import PerceptronFeatureExtractor

        p = PerceptronFeatureExtractor()
        features = p.extract_features({})
        assert features.shape == (1000,)
        assert np.all(features >= 0)

    def test_extract_features_with_content(self, sample_course_content):
        from adaptive_learner.perceptron_model import PerceptronFeatureExtractor

        p = PerceptronFeatureExtractor()
        features = p.extract_features(sample_course_content)
        assert len(features.shape) == 1
        assert features.shape[0] >= 1
        assert p.is_fitted

    def test_learn_patterns(self, sample_course_content):
        from adaptive_learner.perceptron_model import PerceptronFeatureExtractor

        p = PerceptronFeatureExtractor()
        p.learn_patterns([sample_course_content, sample_course_content])
        score = p.predict_importance(sample_course_content)
        assert isinstance(score, (int, float))

    def test_save_load(self, sample_course_content, tmp_path):
        from adaptive_learner.perceptron_model import PerceptronFeatureExtractor

        p1 = PerceptronFeatureExtractor()
        p1.learn_patterns([sample_course_content])
        p1.save(tmp_path / "perceptron.pkl")

        p2 = PerceptronFeatureExtractor()
        p2.load(tmp_path / "perceptron.pkl")
        assert p2.is_fitted


class TestRLContextBuilder:
    """Tests for RLContextBuilder."""

    def test_get_state(self, sample_course_content):
        from adaptive_learner.rl_agent import RLContextBuilder

        rl = RLContextBuilder(epsilon=0.0)  # No exploration
        state = rl.get_state(sample_course_content, [])
        assert "2_" in state  # 2 modules
        assert "3_" in state  # 3 items total

    def test_choose_action(self):
        from adaptive_learner.rl_agent import RLContextBuilder

        rl = RLContextBuilder(epsilon=0.0)
        actions = ["add_module_1", "add_module_2"]
        # With epsilon=0 and empty Q-table, should pick first by max
        action = rl.choose_action("2_3_0", actions)
        assert action in actions

    def test_update_q_value(self):
        from adaptive_learner.rl_agent import RLContextBuilder

        rl = RLContextBuilder(learning_rate=0.1)
        rl.update_q_value("s1", "a1", 1.0, "s2", ["a2"])
        assert rl.q_table["s1"]["a1"] != 0

    def test_build_context_iteratively(self, sample_course_content):
        from adaptive_learner.perceptron_model import PerceptronFeatureExtractor
        from adaptive_learner.rl_agent import RLContextBuilder

        perceptron = PerceptronFeatureExtractor()
        perceptron.learn_patterns([sample_course_content])
        rl = RLContextBuilder(epsilon=0.0)
        context = rl.build_context_iteratively(
            sample_course_content, perceptron, max_iterations=3
        )
        assert len(context) <= 3
        assert all(isinstance(c, str) for c in context)


class TestCanvasContentFetcher:
    """Tests for CanvasContentFetcher (with mocked HTTP)."""

    def test_fetch_course_content(self, mock_config, sample_course_content):
        from adaptive_learner.canvas_fetcher import CanvasContentFetcher

        with patch("adaptive_learner.canvas_fetcher.httpx.Client") as mock_client:
            client_instance = MagicMock()
            mock_client.return_value.__enter__.return_value = client_instance

            modules_resp = MagicMock()
            modules_resp.status_code = 200
            modules_resp.json.return_value = [
                {"id": 1, "name": "Intro"},
                {"id": 2, "name": "Week 1"},
            ]
            modules_resp.raise_for_status = MagicMock()

            items_resp = MagicMock()
            items_resp.status_code = 200
            items_resp.json.return_value = [{"id": 1, "title": "Item 1", "type": "Page"}]

            client_instance.get.side_effect = [modules_resp, items_resp, items_resp]

            fetcher = CanvasContentFetcher()
            result = fetcher.fetch_course_content(58606)

            assert result["course_id"] == 58606
            assert len(result["modules"]) == 2

    def test_save_to_folder(self, mock_config, sample_course_content, tmp_path):
        from adaptive_learner.canvas_fetcher import CanvasContentFetcher

        fetcher = CanvasContentFetcher()
        fetcher.save_to_folder(sample_course_content, tmp_path)

        course_dir = tmp_path / "course_58606"
        assert course_dir.exists()
        assert (course_dir / "module_1" / "items.json").exists()
        assert (course_dir / "module_2" / "meta.json").exists()


class TestAdaptiveCourseLearner:
    """Tests for AdaptiveCourseLearner."""

    def test_learn_from_course(
        self, mock_config, sample_course_content, tmp_path
    ):
        from adaptive_learner.learner import AdaptiveCourseLearner

        with patch.object(
            AdaptiveCourseLearner,
            "get_course_content",
            return_value=sample_course_content,
        ):
            learner = AdaptiveCourseLearner(knowledge_base_path=tmp_path)
            # Override fetcher to avoid real fetch
            learner.fetcher.fetch_course_content = lambda cid: sample_course_content

            context = learner.learn_from_course(58606, iterations=2)
            assert isinstance(context, list)
            assert (tmp_path / "course_58606_context.json").exists()
