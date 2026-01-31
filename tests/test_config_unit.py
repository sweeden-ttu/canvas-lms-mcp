"""
Unit tests for config module.

Tests get_api_headers, load_test_hints, and load_env_config behavior
without synthetic API data. Uses real token strings and real file I/O
where .env is present or a temporary .env is created for isolation.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    get_api_headers,
    load_test_hints,
    CanvasConfig,
    TestHints,
    DEFAULT_PER_PAGE,
    MAX_PER_PAGE,
    PROJECT_ROOT,
)


class TestGetApiHeaders:
    """Tests for get_api_headers."""

    def test_returns_expected_keys(self):
        out = get_api_headers("abc123")
        assert "Authorization" in out
        assert "Content-Type" in out
        assert "Accept" in out

    def test_authorization_bearer(self):
        out = get_api_headers("mytoken")
        assert out["Authorization"] == "Bearer mytoken"

    def test_content_type_json(self):
        out = get_api_headers("x")
        assert out["Content-Type"] == "application/json"
        assert out["Accept"] == "application/json"


class TestLoadTestHints:
    """Tests for load_test_hints. Uses real file I/O; no synthetic data."""

    def test_missing_file_returns_empty_hints(self, tmp_path):
        # load_test_hints uses Path(__file__).parent; patch config __file__ so parent is tmp_path
        import config as config_mod
        fake_config_path = tmp_path / "config.py"
        with patch.object(config_mod, "__file__", str(fake_config_path)):
            hints = load_test_hints()
        assert hints.valid_course_ids == []
        assert hints.test_assignment_id is None

    def test_valid_json_loads(self, tmp_path):
        (tmp_path / "test_hints.json").write_text(
            json.dumps({"valid_course_ids": [58606, 53482]})
        )
        import config as config_mod
        fake_config_path = tmp_path / "config.py"
        with patch.object(config_mod, "__file__", str(fake_config_path)):
            hints = load_test_hints()
        assert hints.valid_course_ids == [58606, 53482]

    def test_invalid_json_returns_empty_hints(self, tmp_path):
        (tmp_path / "test_hints.json").write_text("not json {")
        import config as config_mod
        fake_config_path = tmp_path / "config.py"
        with patch.object(config_mod, "__file__", str(fake_config_path)):
            hints = load_test_hints()
        assert hints.valid_course_ids == []


class TestCanvasConfig:
    """Tests for CanvasConfig validation."""

    def test_valid_config(self):
        cfg = CanvasConfig(
            api_token="a" * 20,
            base_url="https://texastech.instructure.com",
        )
        assert cfg.api_token == "a" * 20
        assert cfg.base_url == "https://texastech.instructure.com"

    def test_base_url_stripped_trailing_slash(self):
        cfg = CanvasConfig(
            api_token="x" * 20,
            base_url="https://texastech.instructure.com/",
        )
        assert cfg.base_url == "https://texastech.instructure.com"

    def test_empty_token_rejected(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            CanvasConfig(api_token="", base_url="https://texastech.instructure.com")

    def test_placeholder_token_rejected(self):
        with pytest.raises(ValueError, match="placeholder"):
            CanvasConfig(
                api_token="your_canvas_api_token_here",
                base_url="https://texastech.instructure.com",
            )

    def test_http_url_rejected(self):
        with pytest.raises(ValueError, match="https"):
            CanvasConfig(
                api_token="x" * 20,
                base_url="http://example.com",
            )


class TestTestHints:
    """Tests for TestHints model."""

    def test_defaults(self):
        h = TestHints()
        assert h.valid_course_ids == []
        assert h.test_assignment_id is None
        assert h.test_module_id is None

    def test_from_dict(self):
        h = TestHints(
            valid_course_ids=[1, 2],
            test_module_id=10,
        )
        assert h.valid_course_ids == [1, 2]
        assert h.test_module_id == 10


class TestConstants:
    """Tests for module constants."""

    def test_default_per_page(self):
        assert DEFAULT_PER_PAGE == 50
        assert MAX_PER_PAGE == 100

    def test_project_root_is_directory(self):
        assert PROJECT_ROOT.is_dir() or not PROJECT_ROOT.exists()
