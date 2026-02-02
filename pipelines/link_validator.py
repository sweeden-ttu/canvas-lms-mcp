"""
Link validation pipeline.

Validates HTTP links in markdown, HTML, and config files.
Uses httpx for HEAD requests; integrates with LangSmith for tracing.
"""

import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from pipelines.base import ValidationResult


class LinkValidationPipeline:
    """Pipeline for validating URLs in content."""

    def __init__(self, project_root: Path | None = None, timeout: float = 10.0):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.timeout = timeout

    def extract_links(self, content: str, skip_localhost: bool = True) -> list[str]:
        """Extract HTTP(S) URLs from markdown and HTML."""
        url_pattern = re.compile(r"https?://[^\s)\]>\"']+")
        urls = list(set(url_pattern.findall(content)))
        if skip_localhost:
            urls = [u for u in urls if "localhost" not in u and "127.0.0.1" not in u]
        return urls

    def check_link(self, url: str) -> ValidationResult:
        """Check a single URL (HEAD request)."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme.startswith("http"):
                return ValidationResult(name="link_scheme", passed=False, message=f"Non-HTTP: {url}")

            with httpx.Client(follow_redirects=True, timeout=self.timeout) as client:
                resp = client.head(url)
                passed = 200 <= resp.status_code < 400
                return ValidationResult(
                    name="link_check",
                    passed=passed,
                    message=f"{url}: {resp.status_code}",
                    details={"url": url, "status_code": resp.status_code},
                )
        except httpx.TimeoutException:
            return ValidationResult(name="link_check", passed=False, message=f"Timeout: {url}")
        except Exception as e:
            return ValidationResult(name="link_check", passed=False, message=f"{url}: {e}")

    def validate_file(self, path: Path) -> list[ValidationResult]:
        """Extract and validate all links in a file."""
        content = path.read_text()
        links = self.extract_links(content)
        results = []
        for url in links:
            r = self.check_link(url)
            r.name = f"link_{path.stem}"
            results.append(r)
        return results

    def run(self, patterns: list[str] | None = None) -> list[ValidationResult]:
        """Run link validation on project content."""
        patterns = patterns or ["**/*.md", "**/*.html", "**/*.yml", "**/*.yaml"]
        results: list[ValidationResult] = []

        for pattern in patterns:
            for path in self.project_root.rglob(pattern.lstrip("**/")):
                if path.is_file() and "_site" not in str(path) and ".git" not in str(path):
                    try:
                        results.extend(self.validate_file(path))
                    except Exception as e:
                        results.append(
                            ValidationResult(name="link_scan", passed=False, message=f"{path}: {e}")
                        )

        return results
