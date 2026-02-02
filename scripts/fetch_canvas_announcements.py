#!/usr/bin/env python3
"""
Fetch Canvas LMS announcements and extract TA contacts.

Fetches announcements from configured courses, parses message content for TA
contact information (emails, names in TA/office hours context), and stores
all data in the _data folder.

Usage:
    uv run python scripts/fetch_canvas_announcements.py [--output-dir _data]

Requires CANVAS_API_TOKEN in .env or environment.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import httpx

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_env_config, get_api_headers

# Course IDs: test_hints + CS5374 Spring 2026
DEFAULT_COURSE_IDS = [58606, 53482, 51243, 70713]
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
# TA-related phrases that often precede contact info
TA_PATTERNS = [
    r"\bTA\s*[:\-]\s*([^\n<]+)",
    r"teaching\s+assistant[s]?\s*[:\-]\s*([^\n<]+)",
    r"office\s+hours?\s*[:\-]\s*([^\n<]+)",
    r"contact\s*(?:TA|TAs)?\s*[:\-]\s*([^\n<]+)",
    r"TAs?\s*:\s*([^\n<]+)",
    r"grader[s]?\s*[:\-]\s*([^\n<]+)",
]


def strip_html(html: str) -> str:
    """Remove HTML tags and decode entities."""
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return unescape(text).strip()


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    return list(dict.fromkeys(EMAIL_PATTERN.findall(text)))


def extract_ta_mentions(text: str) -> list[str]:
    """Extract potential TA contact snippets from text."""
    text_lower = text.lower()
    results = []
    for pat in TA_PATTERNS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            snippet = strip_html(m.group(1))
            if snippet and len(snippet) < 200:
                results.append(snippet)
    return results


def extract_ta_contacts(announcements: list[dict]) -> list[dict]:
    """Extract TA contact info from announcements."""
    seen_emails: set[str] = set()
    seen_snippets: set[str] = set()
    contacts: list[dict] = []

    for ann in announcements:
        msg = ann.get("message", "") or ""
        author = ann.get("author") or {}
        plain = strip_html(msg)

        # Emails from message
        for email in extract_emails(msg):
            if email not in seen_emails:
                seen_emails.add(email)
                contacts.append({
                    "email": email,
                    "source": "announcement_message",
                    "announcement_title": ann.get("title"),
                    "announcement_id": ann.get("id"),
                    "course_id": _course_from_context(ann),
                })

        # TA-related snippets
        for snippet in extract_ta_mentions(msg):
            norm = snippet.strip()[:100]
            if norm and norm not in seen_snippets:
                seen_snippets.add(norm)
                snippet_emails = extract_emails(snippet)
                contacts.append({
                    "snippet": norm,
                    "emails": snippet_emails,
                    "source": "announcement_message",
                    "announcement_title": ann.get("title"),
                    "announcement_id": ann.get("id"),
                    "course_id": _course_from_context(ann),
                })

        # Author as potential TA (instructor/TA posting)
        display_name = author.get("display_name") or ann.get("user_name", "")
        if display_name:
            author_url = author.get("html_url", "")
            contacts.append({
                "name": display_name,
                "html_url": author_url,
                "source": "announcement_author",
                "announcement_title": ann.get("title"),
                "announcement_id": ann.get("id"),
                "course_id": _course_from_context(ann),
            })

    return contacts


def _course_from_context(ann: dict) -> int | None:
    """Extract course ID from context_code (e.g. course_51243 -> 51243)."""
    code = ann.get("context_code", "")
    if code.startswith("course_"):
        try:
            return int(code.replace("course_", ""))
        except ValueError:
            pass
    return None


def fetch_announcements(client: httpx.Client, course_ids: list[int], per_page: int = 50) -> list[dict]:
    """Fetch announcements for given courses."""
    context_codes = [f"course_{cid}" for cid in course_ids]
    all_announcements: list[dict] = []
    page = 1

    while True:
        resp = client.get(
            "/api/v1/announcements",
            params={
                "context_codes[]": context_codes,
                "per_page": per_page,
                "page": page,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        all_announcements.extend(data)
        if len(data) < per_page:
            break
        page += 1

    return all_announcements


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Canvas announcements and extract TA contacts")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("_data"),
        help="Output directory (default: _data)",
    )
    parser.add_argument(
        "--course-ids",
        type=str,
        default=",".join(str(c) for c in DEFAULT_COURSE_IDS),
        help="Comma-separated course IDs",
    )
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    course_ids = [int(x.strip()) for x in args.course_ids.split(",") if x.strip()]

    config = load_env_config()
    headers = get_api_headers(config.api_token)

    with httpx.Client(
        base_url=config.base_url,
        headers=headers,
        timeout=60.0,
    ) as client:
        print(f"Fetching announcements for courses: {course_ids}")
        announcements = fetch_announcements(client, course_ids)
        print(f"  Retrieved {len(announcements)} announcements")

        ta_contacts = extract_ta_contacts(announcements)
        print(f"  Extracted {len(ta_contacts)} TA contact entries")

        # Store raw announcements (JSON)
        raw_path = out / "canvas_announcements.json"
        payload = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "course_ids": course_ids,
            "count": len(announcements),
            "announcements": announcements,
        }
        raw_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"  Saved raw announcements to {raw_path}")

        # Store TA contacts (JSON and YAML-like structure)
        contacts_path = out / "canvas_ta_contacts.json"
        contacts_payload = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": "canvas_announcements",
            "course_ids": course_ids,
            "count": len(ta_contacts),
            "contacts": ta_contacts,
        }
        contacts_path.write_text(json.dumps(contacts_payload, indent=2), encoding="utf-8")
        print(f"  Saved TA contacts to {contacts_path}")

        # Also write a simple YAML for nav/readability
        ta_yml_path = out / "canvas_ta_contacts.yml"
        lines = [
            "# TA contacts extracted from Canvas announcements",
            f"# Fetched: {contacts_payload['fetched_at']}",
            "contacts:",
        ]
        for c in ta_contacts:
            parts = []
            if "email" in c:
                parts.append(f"email: {c['email']}")
            if "snippet" in c:
                snip = c["snippet"][:120] + ("..." if len(c["snippet"]) > 120 else "")
                parts.append(f'snippet: "{snip}"')
            if "name" in c:
                parts.append(f'name: "{c["name"]}"')
            lines.append("  - " + ", ".join(parts))
            if c.get("announcement_title") or c.get("course_id"):
                if c.get("announcement_title"):
                    lines.append(f'    announcement_title: "{c["announcement_title"]}"')
                if c.get("course_id"):
                    lines.append(f"    course_id: {c['course_id']}")
        ta_yml_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Saved TA contacts (YAML) to {ta_yml_path}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
