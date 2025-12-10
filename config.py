"""
Configuration module for Canvas LMS MCP Server.

Handles loading of:
- Environment variables from .env (REQUIRED)
- Test hints from test_hints.json (OPTIONAL)

Security: Fails immediately if .env is missing or token is not set.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


class CanvasConfig(BaseModel):
    """Canvas API configuration with validation."""

    api_token: str = Field(..., description="Canvas API Bearer Token")
    base_url: str = Field(
        default="https://texastech.instructure.com",
        description="Canvas instance base URL",
    )

    @field_validator("api_token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Ensure token is not empty or placeholder."""
        if not v or v.strip() == "":
            raise ValueError("CANVAS_API_TOKEN cannot be empty")
        if v == "your_canvas_api_token_here":
            raise ValueError(
                "CANVAS_API_TOKEN is still set to placeholder. "
                "Please update .env with your actual Canvas API token."
            )
        return v.strip()

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL is valid and doesn't have trailing slash."""
        v = v.strip().rstrip("/")
        if not v.startswith("https://"):
            raise ValueError("CANVAS_BASE_URL must start with https://")
        return v


class TestHints(BaseModel):
    """Optional test hints for targeted testing."""

    valid_course_ids: list[int] = Field(default_factory=list)
    test_assignment_id: int | None = None
    test_module_id: int | None = None
    test_discussion_id: int | None = None


def load_env_config() -> CanvasConfig:
    """
    Load Canvas configuration from environment variables.

    Raises:
        SystemExit: If .env file is missing or required variables are not set.

    Returns:
        CanvasConfig: Validated configuration object.
    """
    # Determine project root (where .env should be)
    project_root = Path(__file__).parent

    # Look for .env file
    env_file = project_root / ".env"

    if not env_file.exists():
        print("=" * 60, file=sys.stderr)
        print("CRITICAL ERROR: .env file not found!", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"Expected location: {env_file}", file=sys.stderr)
        print("", file=sys.stderr)
        print("To fix this:", file=sys.stderr)
        print("1. Copy .env.example to .env", file=sys.stderr)
        print("2. Add your Canvas API token to .env", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example .env contents:", file=sys.stderr)
        print("  CANVAS_API_TOKEN=your_actual_token_here", file=sys.stderr)
        print("  CANVAS_BASE_URL=https://texastech.instructure.com", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        sys.exit(1)

    # Load environment variables from .env
    load_dotenv(env_file)

    # Get values from environment
    api_token = os.getenv("CANVAS_API_TOKEN", "")
    base_url = os.getenv("CANVAS_BASE_URL", "https://texastech.instructure.com")

    try:
        return CanvasConfig(api_token=api_token, base_url=base_url)
    except ValueError as e:
        print("=" * 60, file=sys.stderr)
        print("CONFIGURATION ERROR", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(str(e), file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        sys.exit(1)


def load_test_hints() -> TestHints:
    """
    Load test hints from test_hints.json.

    This is optional - if the file doesn't exist or is invalid,
    returns empty hints with a warning.

    Returns:
        TestHints: Test hint configuration (may be empty).
    """
    project_root = Path(__file__).parent
    hints_file = project_root / "test_hints.json"

    if not hints_file.exists():
        print(
            "NOTE: test_hints.json not found. "
            "Some tests may be skipped. Create test_hints.json with valid course IDs for full testing.",
            file=sys.stderr,
        )
        return TestHints()

    try:
        with open(hints_file, "r") as f:
            data = json.load(f)
        return TestHints(**data)
    except json.JSONDecodeError as e:
        print(
            f"WARNING: test_hints.json contains invalid JSON: {e}. Using empty hints.",
            file=sys.stderr,
        )
        return TestHints()
    except Exception as e:
        print(
            f"WARNING: Could not load test_hints.json: {e}. Using empty hints.",
            file=sys.stderr,
        )
        return TestHints()


def get_api_headers(token: str) -> dict[str, str]:
    """
    Generate standard headers for Canvas API requests.

    Args:
        token: Canvas API Bearer token.

    Returns:
        dict: Headers dictionary for httpx requests.
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# Module-level constants for easy import
PROJECT_ROOT = Path(__file__).parent
DEFAULT_PER_PAGE = 50
MAX_PER_PAGE = 100


def get_config() -> tuple[CanvasConfig, TestHints]:
    """
    Convenience function to load all configuration at once.

    Returns:
        tuple: (CanvasConfig, TestHints)
    """
    return load_env_config(), load_test_hints()


if __name__ == "__main__":
    # Test configuration loading
    print("Testing configuration loading...")
    config, hints = get_config()
    print(f"✅ Base URL: {config.base_url}")
    print(f"✅ Token loaded: {'*' * 8}...{config.api_token[-4:]}")
    print(f"✅ Course IDs in hints: {hints.valid_course_ids}")
