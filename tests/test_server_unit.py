"""
Unit tests for MCP server utilities and tool registration.

Tests _format_response, _handle_canvas_error (with real httpx exception types),
and tool registration. Requires .env with valid CANVAS_API_TOKEN so that
server module can be imported (load_env_config runs at import). No synthetic
API response data; error tests use real httpx exception instances.
"""

import asyncio
import sys
from pathlib import Path

import httpx
import pytest

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Skip entire module if .env missing (server import would exit)
_env_file = Path(__file__).resolve().parent.parent / ".env"
if not _env_file.exists():
    pytest.skip(
        "Missing .env; server cannot be imported. Create .env from .env.example to run server unit tests.",
        allow_module_level=True,
    )

from server import (
    _format_response,
    _handle_canvas_error,
    ResponseFormat,
    mcp,
    EmptyInput,
    CourseIdInput,
    ModuleItemsInput,
    FileInput,
)


class TestFormatResponse:
    """Tests for _format_response. Uses minimal valid structures from verified_canvas_spec shape."""

    def test_empty_list_markdown(self):
        out = _format_response([], ResponseFormat.MARKDOWN, "Title")
        assert "## Title" in out
        assert "No items found" in out

    def test_list_of_dicts_markdown(self):
        data = [
            {"id": 1, "name": "Course A", "course_code": "CS-100"},
            {"id": 2, "name": "Course B"},
        ]
        out = _format_response(data, ResponseFormat.MARKDOWN, "Courses")
        assert "Course A" in out
        assert "Course B" in out
        assert "id" in out or "1" in out

    def test_list_json(self):
        data = [{"id": 1, "name": "X"}]
        out = _format_response(data, ResponseFormat.JSON, "")
        assert '"id": 1' in out
        assert '"name": "X"' in out

    def test_dict_markdown(self):
        data = {"id": 58606, "name": "Scott Weeden", "login_id": "sweeden"}
        out = _format_response(data, ResponseFormat.MARKDOWN, "Profile")
        assert "Profile" in out or "id" in out
        assert "58606" in out or "name" in out

    def test_dict_json(self):
        data = {"key": "value"}
        out = _format_response(data, ResponseFormat.JSON, "")
        assert '"key": "value"' in out


class TestHandleCanvasError:
    """Tests for _handle_canvas_error. Uses real httpx exception types."""

    def test_401_message(self):
        request = httpx.Request("GET", "https://texastech.instructure.com/api/v1/users/self/profile")
        response = httpx.Response(401, request=request)
        exc = httpx.HTTPStatusError("Unauthorized", request=request, response=response)
        msg = _handle_canvas_error(exc)
        assert "401" in msg or "Unauthorized" in msg or "token" in msg.lower()

    def test_403_message(self):
        request = httpx.Request("GET", "https://texastech.instructure.com/api/v1/courses/1/files")
        response = httpx.Response(403, request=request)
        exc = httpx.HTTPStatusError("Forbidden", request=request, response=response)
        msg = _handle_canvas_error(exc)
        assert "403" in msg or "Forbidden" in msg or "Permission" in msg

    def test_404_message(self):
        request = httpx.Request("GET", "https://texastech.instructure.com/api/v1/courses/999999/assignments")
        response = httpx.Response(404, request=request)
        exc = httpx.HTTPStatusError("Not Found", request=request, response=response)
        msg = _handle_canvas_error(exc)
        assert "404" in msg or "not found" in msg.lower()

    def test_429_message(self):
        request = httpx.Request("GET", "https://texastech.instructure.com/api/v1/courses")
        response = httpx.Response(429, request=request)
        exc = httpx.HTTPStatusError("Too Many Requests", request=request, response=response)
        msg = _handle_canvas_error(exc)
        assert "429" in msg or "Rate" in msg or "limit" in msg.lower()

    def test_context_prefixed(self):
        request = httpx.Request("GET", "https://example.com/")
        response = httpx.Response(404, request=request)
        exc = httpx.HTTPStatusError("Not Found", request=request, response=response)
        msg = _handle_canvas_error(exc, context="fetching course")
        assert "fetching course" in msg or "Error" in msg

    def test_generic_exception(self):
        msg = _handle_canvas_error(ValueError("bad value"))
        assert "bad value" in msg or "ValueError" in msg


class TestInputModels:
    """Tests for Pydantic input models (validation only; no API calls)."""

    def test_empty_input_defaults(self):
        p = EmptyInput()
        assert p.response_format == ResponseFormat.MARKDOWN

    def test_course_id_input_valid(self):
        p = CourseIdInput(course_id=58606)
        assert p.course_id == 58606
        assert p.per_page == 50

    def test_course_id_input_invalid(self):
        with pytest.raises(Exception):  # ValidationError
            CourseIdInput(course_id=0)
        with pytest.raises(Exception):
            CourseIdInput(course_id=-1)

    def test_module_items_input_valid(self):
        p = ModuleItemsInput(course_id=58606, module_id=1)
        assert p.course_id == 58606
        assert p.module_id == 1

    def test_file_input_without_course_id(self):
        p = FileInput(file_id=12345)
        assert p.file_id == 12345
        assert p.course_id is None


class TestToolRegistration:
    """Tests that MCP server exposes expected tools."""

    def test_tools_registered(self):
        tools = asyncio.run(mcp.list_tools())
        names = [t.name for t in tools]
        assert "canvas_get_profile" in names
        assert "canvas_list_courses" in names
        assert "canvas_get_assignments" in names
        assert "canvas_get_modules" in names
        assert "canvas_list_module_items" in names
        assert "canvas_get_course_file" in names
        assert "canvas_get_file_download_url" in names
        assert "canvas_list_planner_items" in names

    def test_expected_tool_count(self):
        tools = asyncio.run(mcp.list_tools())
        # Server has many tools; at least the core set
        assert len(tools) >= 15
