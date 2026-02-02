"""
Content validation pipeline.

Validates course content, Jekyll pages, and generated artifacts for:
- Required front matter and structure
- Schema conformance (syllabus, manifest)
- Completeness and consistency
"""

import json
import re
from pathlib import Path

from pipelines.base import ValidationResult


class ContentValidationPipeline:
    """Pipeline for validating content structure and schema."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent

    def validate_manifest(self, manifest_path: Path) -> ValidationResult:
        """Validate course manifest.json schema."""
        path = self.project_root / manifest_path if not manifest_path.is_absolute() else manifest_path
        if not path.exists():
            return ValidationResult(name="manifest_exists", passed=False, message=f"Manifest not found: {path}")

        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            return ValidationResult(name="manifest_valid_json", passed=False, message=str(e))

        required = ["course_id", "course_name", "syllabus_file", "modules"]
        missing = [k for k in required if k not in data]
        if missing:
            return ValidationResult(name="manifest_required_fields", passed=False, message=f"Missing: {missing}")

        if not isinstance(data.get("modules"), list):
            return ValidationResult(name="manifest_modules_list", passed=False, message="modules must be a list")

        return ValidationResult(
            name="manifest_valid",
            passed=True,
            message=f"Manifest valid: {len(data['modules'])} modules",
            details={"course_id": data.get("course_id"), "course_name": data.get("course_name")},
        )

    def validate_jekyll_front_matter(self, content: str) -> ValidationResult:
        """Validate Jekyll front matter presence and format."""
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not fm_match:
            return ValidationResult(name="jekyll_front_matter", passed=False, message="No front matter found")

        fm = fm_match.group(1)
        if "layout:" not in fm and "title:" not in fm:
            return ValidationResult(name="jekyll_required_fields", passed=False, message="Missing layout or title")

        return ValidationResult(name="jekyll_front_matter", passed=True, message="Valid front matter")

    def validate_syllabus_schema(self, data: dict) -> ValidationResult:
        """Validate course/syllabus object against schema."""
        required = ["id", "name"]
        missing = [k for k in required if k not in data]
        if missing:
            return ValidationResult(name="syllabus_required", passed=False, message=f"Missing: {missing}")

        if "syllabus_body" in data and data["syllabus_body"] and not isinstance(data["syllabus_body"], str):
            return ValidationResult(name="syllabus_body_type", passed=False, message="syllabus_body must be string")

        return ValidationResult(name="syllabus_schema", passed=True, message="Schema valid")

    def run(self, manifest_path: Path | str | None = None) -> list[ValidationResult]:
        """Run full content validation pipeline."""
        manifest_path = manifest_path or "course_content/CS5374-Spring2026/manifest.json"
        results: list[ValidationResult] = []
        path = Path(manifest_path)

        results.append(self.validate_manifest(path))

        jekyll_dir = self.project_root / "jekyll_site"
        if jekyll_dir.exists():
            for md_file in jekyll_dir.rglob("*.md"):
                if md_file.name == "README.md":
                    continue  # README often has no front matter
                content = md_file.read_text()
                r = self.validate_jekyll_front_matter(content)
                results.append(ValidationResult(name=f"jekyll_{md_file.stem}", passed=r.passed, message=r.message))

        return results
