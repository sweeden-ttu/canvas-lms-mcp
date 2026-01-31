#!/usr/bin/env python3
"""
Download CS5374 (Software Verification and Validation) course content from Canvas.

Fetches syllabus, modules, module items, downloads all files, and organizes
with the Mediasite lecture channel link.

Usage:
    uv run python scripts/download_course_content.py [--output-dir DIR]

Requires CANVAS_API_TOKEN in .env or environment.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import httpx

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_env_config, get_api_headers

# CS5374 Spring 2026 - Software Verification and Validation
COURSE_ID = 70713
MEDIASITE_LECTURE_URL = "https://engrmediacast.ttu.edu/Mediasite/Channel/96542-cs5374-d01-namin-spring-2026/browse/null/most-recent/null/0/null"

# Module structure from Canvas (id -> sanitized folder name)
MODULES = [
    (811209, "01_Video_Channel"),
    (811217, "02_Outline_Syllabus"),
    (811245, "03_Lecture_Notes_Software_Testing"),
    (811248, "04_LangSmith_Tutorial_1"),
    (811331, "05_LangSmith_Tutorial_2"),
    (813151, "06_OpenSource_Tools_AI_LLM_RL"),
    (816046, "07_LangGraph_Hands_On"),
]


def sanitize_filename(name: str) -> str:
    """Make filename safe for filesystem."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name.strip()[:200]


def fetch_course_with_syllabus(client: httpx.Client) -> dict:
    """Get course details including syllabus_body."""
    resp = client.get(
        f"/api/v1/courses/{COURSE_ID}",
        params={"include[]": ["syllabus_body"]},
    )
    resp.raise_for_status()
    return resp.json()


def fetch_modules(client: httpx.Client) -> list:
    """Get all modules for the course."""
    resp = client.get(
        f"/api/v1/courses/{COURSE_ID}/modules",
        params={"per_page": 100},
    )
    resp.raise_for_status()
    return resp.json()


def fetch_module_items(client: httpx.Client, module_id: int) -> list:
    """Get items in a module."""
    resp = client.get(
        f"/api/v1/courses/{COURSE_ID}/modules/{module_id}/items",
        params={"per_page": 100},
    )
    resp.raise_for_status()
    return resp.json()


def get_file_download_url(client: httpx.Client, file_id: int) -> str:
    """Get temporary download URL for a file."""
    resp = client.get(f"/api/v1/files/{file_id}/public_url")
    resp.raise_for_status()
    data = resp.json()
    return data.get("public_url") or data.get("url", "")


def download_file(url: str, dest: Path) -> None:
    """Download file from URL (use vanilla client - public URLs are pre-signed)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True, timeout=60.0) as dl_client:
        with dl_client.stream("GET", url) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download CS5374 course content")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("course_content/CS5374-Spring2026"),
        help="Output directory",
    )
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    config = load_env_config()
    headers = get_api_headers(config.api_token)

    with httpx.Client(
        base_url=config.base_url,
        headers=headers,
        timeout=60.0,
        follow_redirects=True,
    ) as client:
        # 1. Fetch course with syllabus
        print("Fetching course and syllabus...")
        course = fetch_course_with_syllabus(client)
        syllabus_body = course.get("syllabus_body", "")
        course_name = course.get("name", "CS5374")

        syllabus_path = out / "syllabus.html"
        syllabus_path.write_text(syllabus_body or "<p>No syllabus content.</p>", encoding="utf-8")
        print(f"  Saved syllabus to {syllabus_path}")

        # 2. Create manifest with Mediasite link
        manifest = {
            "course_id": COURSE_ID,
            "course_name": course_name,
            "syllabus_file": "syllabus.html",
            "mediasite_lectures": MEDIASITE_LECTURE_URL,
            "modules": [],
        }

        # 3. Fetch modules and items, download files
        modules_data = fetch_modules(client)
        module_by_id = {m["id"]: m for m in modules_data}

        for module_id, folder_name in MODULES:
            mod = module_by_id.get(module_id)
            if not mod:
                continue

            module_path = out / folder_name
            module_path.mkdir(exist_ok=True)

            items = fetch_module_items(client, module_id)
            module_manifest = {"name": mod["name"], "folder": folder_name, "items": []}

            for item in items:
                title = item.get("title", "Untitled")
                item_type = item.get("type", "")
                if item_type == "File" and item.get("content_id"):
                    file_id = item["content_id"]
                    try:
                        dl_url = get_file_download_url(client, file_id)
                        if dl_url:
                            filename = sanitize_filename(title)
                            dest = module_path / filename
                            download_file(dl_url, dest)
                            module_manifest["items"].append({"title": title, "file": filename})
                            print(f"  Downloaded: {folder_name}/{filename}")
                    except Exception as e:
                        print(f"  ERROR downloading {title}: {e}", file=sys.stderr)
                        module_manifest["items"].append({"title": title, "error": str(e)})
                elif item_type == "ExternalUrl":
                    url = item.get("external_url", "")
                    if "mediasite" in url.lower():
                        link_file = module_path / "LECTURES_MEDIASITE_LINK.txt"
                        link_file.write_text(f"Video Lectures:\n{url}\n", encoding="utf-8")
                        module_manifest["items"].append({"title": title, "url": url})
                        print(f"  Linked: {folder_name} -> Mediasite")

            manifest["modules"].append(module_manifest)

        # 4. Write manifest and README
        manifest_path = out / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        readme = f"""# {course_name}

## Syllabus
See `syllabus.html`

## Lecture Videos (Mediasite)
{MEDIASITE_LECTURE_URL}

## Module Structure
"""
        for m in manifest["modules"]:
            readme += f"\n### {m['name']} (`{m['folder']}/`)\n"
            for it in m["items"]:
                if "file" in it:
                    readme += f"- {it['title']}\n"
                elif "url" in it:
                    readme += f"- [Lecture Videos]({it['url']})\n"

        (out / "README.md").write_text(readme, encoding="utf-8")
        print(f"\nDone. Content in {out.absolute()}")
        print(f"Manifest: {manifest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
