"""
Pytest configuration and shared fixtures.

Mocks Canvas config to allow tests to run without .env.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock config before any module imports it - prevents sys.exit when .env missing
_config_mock = MagicMock()
_config_mock.base_url = "https://test.instructure.com"
_config_mock.api_token = "test-token"

_headers_mock = {
    "Authorization": "Bearer test-token",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def _mock_load_env_config():
    return _config_mock


def _mock_get_api_headers(_token=None):
    return _headers_mock


# Patch config module so canvas_fetcher gets mocked functions
patch("config.load_env_config", _mock_load_env_config).start()
patch("config.get_api_headers", _mock_get_api_headers).start()
