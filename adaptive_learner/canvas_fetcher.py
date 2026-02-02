"""
Canvas Content Fetcher - Downloads course materials via Canvas API.

Uses CANVAS_API_TOKEN from environment (loaded via config.py).
"""

import json
from pathlib import Path

import httpx

# Import from parent project - ensure project root is on path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_env_config, get_api_headers


class CanvasContentFetcher:
    """Fetches course and module content from Canvas LMS."""

    def __init__(self):
        self.config = load_env_config()

    def _get_client(self) -> httpx.Client:
        """Create a synchronous HTTP client with Canvas authentication."""
        return httpx.Client(
            base_url=self.config.base_url,
            headers=get_api_headers(self.config.api_token),
            timeout=60.0,
        )

    def fetch_course_content(self, course_id: int) -> dict:
        """
        Fetch full course content including all modules and their items.

        Args:
            course_id: Canvas course ID

        Returns:
            dict with keys: course_id, modules (list of modules with items)
        """
        with self._get_client() as client:
            modules_resp = client.get(
                f"/api/v1/courses/{course_id}/modules",
                params={"per_page": 100, "include": ["items"]},
            )
            modules_resp.raise_for_status()
            modules = modules_resp.json()

            # Fetch items for each module (include param may not return full items)
            for module in modules:
                items_resp = client.get(
                    f"/api/v1/courses/{course_id}/modules/{module['id']}/items",
                    params={"per_page": 100},
                )
                if items_resp.status_code == 200:
                    module["items"] = items_resp.json()
                else:
                    module["items"] = []

            return {"course_id": course_id, "modules": modules}

    def fetch_courses(self, enrollment_state: str = "active") -> list:
        """Fetch list of enrolled courses."""
        with self._get_client() as client:
            resp = client.get(
                "/api/v1/courses",
                params={
                    "enrollment_state": enrollment_state,
                    "per_page": 100,
                },
            )
            resp.raise_for_status()
            return resp.json()

    def save_to_folder(self, content: dict, base_path: Path) -> None:
        """Save course content to knowledge base folder structure."""
        course_path = base_path / f"course_{content['course_id']}"
        course_path.mkdir(parents=True, exist_ok=True)
        for module in content.get("modules", []):
            module_path = course_path / f"module_{module['id']}"
            module_path.mkdir(exist_ok=True)
            (module_path / "items.json").write_text(
                json.dumps(module.get("items", []), indent=2)
            )
            (module_path / "meta.json").write_text(
                json.dumps(
                    {k: v for k, v in module.items() if k != "items"},
                    indent=2,
                )
            )
