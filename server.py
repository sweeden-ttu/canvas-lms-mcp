#!/usr/bin/env python3
"""
Canvas LMS MCP Server

An MCP (Model Context Protocol) server that provides secure access to Canvas LMS
at Texas Tech University. Compatible with multiple MCP clients including Claude,
Cline, Cursor, and Gemini CLI.

This server exposes ONLY endpoints that have been verified to work via live API tests.
Endpoints that returned 403 Forbidden (like /files) are intentionally NOT implemented.

Usage:
    # Run with stdio transport (default - for Claude Desktop/Claude Code/Cline/Cursor)
    uv run python server.py

    # Run with SSE transport (alternative for Cursor)
    uv run python server.py --transport sse --port 8000

    # Run with HTTP transport (for MCP Inspector debugging)
    uv run python server.py --transport streamable-http --port 8000

Supported MCP Clients:
    - Claude Desktop (stdio)
    - Claude Code (stdio)
    - Cline for VS Code (stdio)
    - Cursor (stdio or SSE)
    - Gemini CLI (stdio)
    - VS Code with GitHub Copilot (stdio)

Author: Canvas LMS MCP Project
"""

import json
import sys
from enum import Enum
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

from config import load_env_config, get_api_headers, DEFAULT_PER_PAGE, MAX_PER_PAGE


# =============================================================================
# Initialize MCP Server
# =============================================================================

mcp = FastMCP(
    name="canvas_mcp",
)

# Load configuration at startup
_config = load_env_config()


# =============================================================================
# Shared Utilities
# =============================================================================

class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


def _get_client() -> httpx.AsyncClient:
    """Create an HTTP client with Canvas authentication."""
    return httpx.AsyncClient(
        base_url=_config.base_url,
        headers=get_api_headers(_config.api_token),
        timeout=30.0,
    )


def _handle_canvas_error(e: Exception, context: str = "") -> str:
    """
    Format Canvas API errors into actionable messages.
    
    Args:
        e: The exception that occurred
        context: Additional context about what was being attempted
        
    Returns:
        Human-readable error message with suggested fixes
    """
    prefix = f"Error {context}: " if context else "Error: "
    
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return (
                f"{prefix}Invalid API token (401 Unauthorized). "
                "Please check CANVAS_API_TOKEN in your .env file. "
                "You may need to generate a new token in Canvas Settings."
            )
        elif status == 403:
            return (
                f"{prefix}Permission denied (403 Forbidden). "
                "Your account may not have access to this resource. "
                "This is common for student accounts accessing instructor-only endpoints."
            )
        elif status == 404:
            return (
                f"{prefix}Resource not found (404). "
                "Please verify the course_id or resource ID is correct."
            )
        elif status == 429:
            return (
                f"{prefix}Rate limit exceeded (429). "
                "Canvas limits API requests. Please wait a few minutes before retrying."
            )
        elif status >= 500:
            return (
                f"{prefix}Canvas server error ({status}). "
                "This is a temporary issue with Canvas. Please try again later."
            )
        return f"{prefix}HTTP {status}: {e.response.reason_phrase}"
    
    elif isinstance(e, httpx.TimeoutException):
        return (
            f"{prefix}Request timed out. "
            "Canvas may be experiencing high load. Please try again."
        )
    elif isinstance(e, httpx.RequestError):
        return f"{prefix}Network error: {str(e)}"
    
    return f"{prefix}{type(e).__name__}: {str(e)}"


def _format_response(data: Any, format: ResponseFormat, title: str = "") -> str:
    """
    Format API response data based on requested format.
    
    Args:
        data: The data to format
        format: Desired output format
        title: Optional title for markdown format
        
    Returns:
        Formatted string
    """
    if format == ResponseFormat.JSON:
        return json.dumps(data, indent=2, default=str)
    
    # Markdown format
    lines = []
    if title:
        lines.append(f"## {title}\n")
    
    if isinstance(data, list):
        if not data:
            lines.append("*No items found.*")
        else:
            for i, item in enumerate(data, 1):
                if isinstance(item, dict):
                    name = item.get("name") or item.get("title") or item.get("id", f"Item {i}")
                    lines.append(f"**{i}. {name}**")
                    for key, value in item.items():
                        if key not in ("name", "title") and value is not None:
                            # Skip large nested objects
                            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                                continue
                            lines.append(f"  - {key}: {value}")
                    lines.append("")
                else:
                    lines.append(f"- {item}")
    elif isinstance(data, dict):
        for key, value in data.items():
            if value is not None:
                lines.append(f"- **{key}**: {value}")
    else:
        lines.append(str(data))
    
    return "\n".join(lines)


# =============================================================================
# Pydantic Input Models
# =============================================================================

class EmptyInput(BaseModel):
    """Input model for tools that take no parameters."""
    model_config = ConfigDict(extra='forbid')
    
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class CourseIdInput(BaseModel):
    """Input model for tools that require a course ID."""
    model_config = ConfigDict(extra='forbid')
    
    course_id: int = Field(
        ...,
        description="Canvas course ID (e.g., 58606). Find this in the URL when viewing a course.",
        gt=0,
    )
    per_page: int = Field(
        default=DEFAULT_PER_PAGE,
        description="Number of items to return per page",
        ge=1,
        le=MAX_PER_PAGE,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class AnnouncementsInput(BaseModel):
    """Input model for announcements tool."""
    model_config = ConfigDict(extra='forbid')
    
    course_ids: list[int] = Field(
        ...,
        description="List of course IDs to get announcements from (e.g., [58606, 53482])",
        min_length=1,
    )
    per_page: int = Field(
        default=DEFAULT_PER_PAGE,
        description="Number of announcements to return",
        ge=1,
        le=MAX_PER_PAGE,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class ListCoursesInput(BaseModel):
    """Input model for listing courses."""
    model_config = ConfigDict(extra='forbid')
    
    enrollment_state: str = Field(
        default="active",
        description="Filter by enrollment state: 'active', 'completed', or 'all'",
        pattern="^(active|completed|all)$",
    )
    per_page: int = Field(
        default=DEFAULT_PER_PAGE,
        description="Number of courses to return",
        ge=1,
        le=MAX_PER_PAGE,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class ModuleItemsInput(BaseModel):
    """Input for listing module items."""
    model_config = ConfigDict(extra='forbid')
    
    course_id: int = Field(..., description="Canvas course ID", gt=0)
    module_id: int = Field(..., description="Canvas module ID", gt=0)
    per_page: int = Field(default=DEFAULT_PER_PAGE, ge=1, le=MAX_PER_PAGE)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class FileInput(BaseModel):
    """Input for file operations."""
    model_config = ConfigDict(extra='forbid')
    
    file_id: int = Field(..., description="Canvas file ID", gt=0)
    course_id: Optional[int] = Field(None, description="Course ID (optional, for context)", gt=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CalendarEventInput(BaseModel):
    """Input for creating calendar events."""
    model_config = ConfigDict(extra='forbid')
    
    title: str = Field(..., description="Event title", min_length=1)
    start_at: str = Field(..., description="Start datetime (ISO 8601)")
    end_at: Optional[str] = Field(None, description="End datetime (ISO 8601)")
    description: Optional[str] = Field(None, description="Event description")
    location_name: Optional[str] = Field(None, description="Location name")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CalendarEventListInput(BaseModel):
    """Input for listing calendar events."""
    model_config = ConfigDict(extra='forbid')
    
    start_date: Optional[str] = Field(None, description="Start date filter (ISO 8601)")
    end_date: Optional[str] = Field(None, description="End date filter (ISO 8601)")
    context_codes: Optional[list[str]] = Field(None, description="Context codes to filter (e.g., ['user_self'])")
    per_page: int = Field(default=DEFAULT_PER_PAGE, ge=1, le=MAX_PER_PAGE)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CalendarEventIdInput(BaseModel):
    """Input for calendar event operations requiring an ID."""
    model_config = ConfigDict(extra='forbid')
    
    event_id: int = Field(..., description="Calendar event ID", gt=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CalendarEventUpdateInput(BaseModel):
    """Input for updating calendar events."""
    model_config = ConfigDict(extra='forbid')
    
    event_id: int = Field(..., description="Calendar event ID", gt=0)
    title: Optional[str] = Field(None, description="Event title", min_length=1)
    start_at: Optional[str] = Field(None, description="Start datetime (ISO 8601)")
    end_at: Optional[str] = Field(None, description="End datetime (ISO 8601)")
    description: Optional[str] = Field(None, description="Event description")
    location_name: Optional[str] = Field(None, description="Location name")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class PlannerNoteInput(BaseModel):
    """Input for creating/updating planner notes."""
    model_config = ConfigDict(extra='forbid')
    
    title: str = Field(..., description="Note title", min_length=1)
    details: Optional[str] = Field(None, description="Note details/description")
    todo_date: str = Field(..., description="Date to show on planner (ISO 8601)")
    course_id: Optional[int] = Field(None, description="Associated course ID (optional)", gt=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class PlannerNoteIdInput(BaseModel):
    """Input for planner note operations requiring an ID."""
    model_config = ConfigDict(extra='forbid')
    
    note_id: int = Field(..., description="Planner note ID", gt=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class PlannerNoteUpdateInput(BaseModel):
    """Input for updating planner notes."""
    model_config = ConfigDict(extra='forbid')
    
    note_id: int = Field(..., description="Planner note ID", gt=0)
    title: Optional[str] = Field(None, description="Note title", min_length=1)
    details: Optional[str] = Field(None, description="Note details/description")
    todo_date: Optional[str] = Field(None, description="Date to show on planner (ISO 8601)")
    course_id: Optional[int] = Field(None, description="Associated course ID (optional)", gt=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class PlannerItemsInput(BaseModel):
    """Input for listing planner items."""
    model_config = ConfigDict(extra='forbid')
    
    start_date: Optional[str] = Field(None, description="Start date filter (ISO 8601)")
    end_date: Optional[str] = Field(None, description="End date filter (ISO 8601)")
    per_page: int = Field(default=DEFAULT_PER_PAGE, ge=1, le=MAX_PER_PAGE)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# =============================================================================
# MCP Tools - User Level (No Course ID Required)
# =============================================================================

@mcp.tool(
    name="canvas_get_profile",
    annotations={
        "title": "Get Canvas User Profile",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_profile(params: EmptyInput) -> str:
    """
    Get the current user's Canvas profile.
    
    Returns profile information including name, email, and login ID.
    This is useful for verifying API connectivity and identifying the current user.
    
    Args:
        params (EmptyInput): Optional response format parameter
        
    Returns:
        str: User profile data in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get("/api/v1/users/self/profile")
            response.raise_for_status()
            data = response.json()
            return _format_response(data, params.response_format, "Your Canvas Profile")
        except Exception as e:
            return _handle_canvas_error(e, "fetching profile")


@mcp.tool(
    name="canvas_list_courses",
    annotations={
        "title": "List Canvas Courses",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_list_courses(params: ListCoursesInput) -> str:
    """
    List courses the user is enrolled in.
    
    Returns a list of courses with their IDs, names, and enrollment information.
    Use the course IDs from this response for other course-specific tools.
    
    Args:
        params (ListCoursesInput): Filter and pagination options
        
    Returns:
        str: List of courses in requested format
    """
    async with _get_client() as client:
        try:
            query_params = {
                "per_page": params.per_page,
            }
            if params.enrollment_state != "all":
                query_params["enrollment_state"] = params.enrollment_state
            
            response = await client.get("/api/v1/courses", params=query_params)
            response.raise_for_status()
            data = response.json()
            return _format_response(data, params.response_format, "Your Canvas Courses")
        except Exception as e:
            return _handle_canvas_error(e, "listing courses")


@mcp.tool(
    name="canvas_get_todo",
    annotations={
        "title": "Get Canvas To-Do Items",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_todo(params: EmptyInput) -> str:
    """
    Get the user's Canvas to-do items.
    
    Returns pending assignments, quizzes, and other items that need attention.
    This is useful for understanding what work is due soon.
    
    Args:
        params (EmptyInput): Optional response format parameter
        
    Returns:
        str: To-do items in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                "/api/v1/users/self/todo",
                params={"per_page": DEFAULT_PER_PAGE}
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(data, params.response_format, "Your To-Do Items")
        except Exception as e:
            return _handle_canvas_error(e, "fetching to-do items")


@mcp.tool(
    name="canvas_get_upcoming_events",
    annotations={
        "title": "Get Upcoming Events",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_upcoming_events(params: EmptyInput) -> str:
    """
    Get upcoming calendar events for the user.
    
    Returns scheduled events, assignment due dates, and other calendar items.
    Useful for planning and understanding upcoming deadlines.
    
    Args:
        params (EmptyInput): Optional response format parameter
        
    Returns:
        str: Upcoming events in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                "/api/v1/users/self/upcoming_events",
                params={"per_page": DEFAULT_PER_PAGE}
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(data, params.response_format, "Upcoming Events")
        except Exception as e:
            return _handle_canvas_error(e, "fetching upcoming events")


# =============================================================================
# MCP Tools - Course Level (Require Course ID)
# =============================================================================

@mcp.tool(
    name="canvas_get_assignments",
    annotations={
        "title": "Get Course Assignments",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_assignments(params: CourseIdInput) -> str:
    """
    Get assignments for a specific course.
    
    Returns assignment details including due dates, points possible, and submission status.
    Use canvas_list_courses first to find valid course IDs.
    
    Args:
        params (CourseIdInput): Course ID and pagination options
        
    Returns:
        str: Assignment list in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                f"/api/v1/courses/{params.course_id}/assignments",
                params={
                    "per_page": params.per_page,
                    "order_by": "due_at",
                }
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data, 
                params.response_format, 
                f"Assignments for Course {params.course_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"fetching assignments for course {params.course_id}")


@mcp.tool(
    name="canvas_get_modules",
    annotations={
        "title": "Get Course Modules",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_modules(params: CourseIdInput) -> str:
    """
    Get modules for a specific course.
    
    Returns the course module structure, which organizes content into units or weeks.
    Use canvas_list_courses first to find valid course IDs.
    
    Args:
        params (CourseIdInput): Course ID and pagination options
        
    Returns:
        str: Module list in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                f"/api/v1/courses/{params.course_id}/modules",
                params={"per_page": params.per_page}
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data, 
                params.response_format, 
                f"Modules for Course {params.course_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"fetching modules for course {params.course_id}")


@mcp.tool(
    name="canvas_get_discussions",
    annotations={
        "title": "Get Discussion Topics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_discussions(params: CourseIdInput) -> str:
    """
    Get discussion topics for a specific course.
    
    Returns discussion boards, their titles, and message counts.
    Use canvas_list_courses first to find valid course IDs.
    
    Args:
        params (CourseIdInput): Course ID and pagination options
        
    Returns:
        str: Discussion topics in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                f"/api/v1/courses/{params.course_id}/discussion_topics",
                params={"per_page": params.per_page}
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data, 
                params.response_format, 
                f"Discussion Topics for Course {params.course_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"fetching discussions for course {params.course_id}")


@mcp.tool(
    name="canvas_get_grades",
    annotations={
        "title": "Get Course Grades",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_grades(params: CourseIdInput) -> str:
    """
    Get grades/enrollment information for a specific course.
    
    Returns your enrollment status and current grades in the course.
    Use canvas_list_courses first to find valid course IDs.
    
    Args:
        params (CourseIdInput): Course ID (per_page not applicable)
        
    Returns:
        str: Enrollment/grade information in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                f"/api/v1/courses/{params.course_id}/enrollments",
                params={
                    "user_id": "self",
                    "type[]": "StudentEnrollment",
                }
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data, 
                params.response_format, 
                f"Your Grades in Course {params.course_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"fetching grades for course {params.course_id}")


@mcp.tool(
    name="canvas_get_announcements",
    annotations={
        "title": "Get Announcements",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_announcements(params: AnnouncementsInput) -> str:
    """
    Get announcements from one or more courses.
    
    Returns recent announcements posted by instructors.
    Use canvas_list_courses first to find valid course IDs.
    
    Args:
        params (AnnouncementsInput): Course IDs and pagination options
        
    Returns:
        str: Announcements in requested format
    """
    async with _get_client() as client:
        try:
            # Canvas expects context_codes[] as repeated params
            context_codes = [f"course_{cid}" for cid in params.course_ids]
            
            response = await client.get(
                "/api/v1/announcements",
                params={
                    "context_codes[]": context_codes,
                    "per_page": params.per_page,
                }
            )
            response.raise_for_status()
            data = response.json()
            course_list = ", ".join(str(cid) for cid in params.course_ids)
            return _format_response(
                data, 
                params.response_format, 
                f"Announcements from Courses {course_list}"
            )
        except Exception as e:
            return _handle_canvas_error(e, "fetching announcements")


# =============================================================================
# MCP Tools - Files/Modules (Read-only for Students)
# =============================================================================

@mcp.tool(
    name="canvas_list_module_items",
    annotations={
        "title": "List Module Items",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_list_module_items(params: ModuleItemsInput) -> str:
    """
    List items within a specific course module.
    
    Returns all items in a module, including files, assignments, discussions, etc.
    Module items can be of type "File" and include a content_id referencing the file.
    
    Args:
        params (ModuleItemsInput): Course ID, module ID, and pagination options
        
    Returns:
        str: Module items in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                f"/api/v1/courses/{params.course_id}/modules/{params.module_id}/items",
                params={"per_page": params.per_page}
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                f"Module Items for Module {params.module_id} in Course {params.course_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"fetching module items for module {params.module_id}")


@mcp.tool(
    name="canvas_get_course_file",
    annotations={
        "title": "Get Course File Metadata",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_course_file(params: FileInput) -> str:
    """
    Get file metadata for a course file.
    
    Returns file information including name, size, content-type, and download URL.
    Students can only access files they have permission to view (published files in unlocked modules).
    
    Args:
        params (FileInput): File ID and optional course ID
        
    Returns:
        str: File metadata in requested format
    """
    async with _get_client() as client:
        try:
            if params.course_id:
                url = f"/api/v1/courses/{params.course_id}/files/{params.file_id}"
            else:
                url = f"/api/v1/files/{params.file_id}"
            
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                f"File {params.file_id} Metadata"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"fetching file {params.file_id}")


@mcp.tool(
    name="canvas_get_file_download_url",
    annotations={
        "title": "Get File Download URL",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_get_file_download_url(params: FileInput) -> str:
    """
    Get a temporary public download URL for a file.
    
    Returns a URL that can be used to download the file. The URL may include
    a verifier parameter for authentication. Students can only download files
    they have permission to view.
    
    Args:
        params (FileInput): File ID
        
    Returns:
        str: Download URL information in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(f"/api/v1/files/{params.file_id}/public_url")
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                f"Download URL for File {params.file_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"fetching download URL for file {params.file_id}")


# =============================================================================
# MCP Tools - Calendar (Personal Calendar Only)
# =============================================================================

@mcp.tool(
    name="canvas_list_calendar_events",
    annotations={
        "title": "List Calendar Events",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_list_calendar_events(params: CalendarEventListInput) -> str:
    """
    List calendar events for the current user.
    
    Returns personal calendar events. Students can only view their own personal
    calendar events, not course calendar events (which are managed by instructors).
    
    Args:
        params (CalendarEventListInput): Date filters and pagination options
        
    Returns:
        str: Calendar events in requested format
    """
    async with _get_client() as client:
        try:
            query_params = {"per_page": params.per_page}
            if params.start_date:
                query_params["start_date"] = params.start_date
            if params.end_date:
                query_params["end_date"] = params.end_date
            if params.context_codes:
                query_params["context_codes[]"] = params.context_codes
            
            response = await client.get("/api/v1/calendar_events", params=query_params)
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                "Your Calendar Events"
            )
        except Exception as e:
            return _handle_canvas_error(e, "listing calendar events")


@mcp.tool(
    name="canvas_create_calendar_event",
    annotations={
        "title": "Create Calendar Event",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def canvas_create_calendar_event(params: CalendarEventInput) -> str:
    """
    Create a personal calendar event.
    
    Creates an event on your personal calendar. Use context_code=user_self to target
    personal calendar. Students can ONLY create/modify their own personal calendar events.
    Students CANNOT add/modify events on course calendars (requires instructor permission).
    
    Args:
        params (CalendarEventInput): Event details (title, start_at, end_at, etc.)
        
    Returns:
        str: Created event in requested format
    """
    async with _get_client() as client:
        try:
            event_data = {
                "calendar_event": {
                    "context_code": "user_self",
                    "title": params.title,
                    "start_at": params.start_at,
                }
            }
            if params.end_at:
                event_data["calendar_event"]["end_at"] = params.end_at
            if params.description:
                event_data["calendar_event"]["description"] = params.description
            if params.location_name:
                event_data["calendar_event"]["location_name"] = params.location_name
            
            response = await client.post("/api/v1/calendar_events", json=event_data)
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                "Created Calendar Event"
            )
        except Exception as e:
            return _handle_canvas_error(e, "creating calendar event")


@mcp.tool(
    name="canvas_update_calendar_event",
    annotations={
        "title": "Update Calendar Event",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_update_calendar_event(params: CalendarEventUpdateInput) -> str:
    """
    Update your own calendar event.
    
    Updates an existing personal calendar event. Students can only update their
    own personal calendar events, not course calendar events.
    
    Args:
        params (CalendarEventUpdateInput): Event ID and fields to update
        
    Returns:
        str: Updated event in requested format
    """
    async with _get_client() as client:
        try:
            event_data = {"calendar_event": {}}
            if params.title:
                event_data["calendar_event"]["title"] = params.title
            if params.start_at:
                event_data["calendar_event"]["start_at"] = params.start_at
            if params.end_at:
                event_data["calendar_event"]["end_at"] = params.end_at
            if params.description is not None:
                event_data["calendar_event"]["description"] = params.description
            if params.location_name is not None:
                event_data["calendar_event"]["location_name"] = params.location_name
            
            response = await client.put(
                f"/api/v1/calendar_events/{params.event_id}",
                json=event_data
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                f"Updated Calendar Event {params.event_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"updating calendar event {params.event_id}")


@mcp.tool(
    name="canvas_delete_calendar_event",
    annotations={
        "title": "Delete Calendar Event",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_delete_calendar_event(params: CalendarEventIdInput) -> str:
    """
    Delete your own calendar event.
    
    Permanently deletes a personal calendar event. Students can only delete their
    own personal calendar events, not course calendar events.
    
    Args:
        params (CalendarEventIdInput): Event ID to delete
        
    Returns:
        str: Confirmation message
    """
    async with _get_client() as client:
        try:
            response = await client.delete(f"/api/v1/calendar_events/{params.event_id}")
            response.raise_for_status()
            # Canvas returns 200 OK with empty body on successful delete
            if params.response_format == ResponseFormat.JSON:
                return json.dumps({"status": "deleted", "event_id": params.event_id})
            return f"✅ Successfully deleted calendar event {params.event_id}"
        except Exception as e:
            return _handle_canvas_error(e, f"deleting calendar event {params.event_id}")


# =============================================================================
# MCP Tools - Planner (Full CRUD for Students)
# =============================================================================

@mcp.tool(
    name="canvas_list_planner_items",
    annotations={
        "title": "List Planner Items",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_list_planner_items(params: PlannerItemsInput) -> str:
    """
    List planner items (assignments, events, notes).
    
    Returns aggregated planner items including assignments, calendar events, and
    planner notes in one view. Filter by date range using start_date and end_date.
    
    Args:
        params (PlannerItemsInput): Date filters and pagination options
        
    Returns:
        str: Planner items in requested format
    """
    async with _get_client() as client:
        try:
            query_params = {"per_page": params.per_page}
            if params.start_date:
                query_params["start_date"] = params.start_date
            if params.end_date:
                query_params["end_date"] = params.end_date
            
            response = await client.get("/api/v1/planner/items", params=query_params)
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                "Your Planner Items"
            )
        except Exception as e:
            return _handle_canvas_error(e, "listing planner items")


@mcp.tool(
    name="canvas_list_planner_notes",
    annotations={
        "title": "List Planner Notes",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_list_planner_notes(params: EmptyInput) -> str:
    """
    List planner notes.
    
    Returns personal planner notes that appear on the student planner.
    Planner notes are personal reminders with titles, details, and todo dates.
    
    Args:
        params (EmptyInput): Optional response format parameter
        
    Returns:
        str: Planner notes in requested format
    """
    async with _get_client() as client:
        try:
            response = await client.get(
                "/api/v1/planner_notes",
                params={"per_page": DEFAULT_PER_PAGE}
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                "Your Planner Notes"
            )
        except Exception as e:
            return _handle_canvas_error(e, "listing planner notes")


@mcp.tool(
    name="canvas_create_planner_note",
    annotations={
        "title": "Create Planner Note",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def canvas_create_planner_note(params: PlannerNoteInput) -> str:
    """
    Create a planner note.
    
    Creates a personal reminder that appears on the student planner.
    Planner notes include title, details, todo_date, and optional course_id.
    
    Args:
        params (PlannerNoteInput): Note details
        
    Returns:
        str: Created note in requested format
    """
    async with _get_client() as client:
        try:
            note_data = {
                "title": params.title,
                "todo_date": params.todo_date,
            }
            if params.details:
                note_data["details"] = params.details
            if params.course_id:
                note_data["course_id"] = params.course_id
            
            response = await client.post("/api/v1/planner_notes", json=note_data)
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                "Created Planner Note"
            )
        except Exception as e:
            return _handle_canvas_error(e, "creating planner note")


@mcp.tool(
    name="canvas_update_planner_note",
    annotations={
        "title": "Update Planner Note",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_update_planner_note(params: PlannerNoteUpdateInput) -> str:
    """
    Update a planner note.
    
    Updates an existing planner note. All fields are optional - only provided
    fields will be updated.
    
    Args:
        params (PlannerNoteUpdateInput): Note ID and fields to update
        
    Returns:
        str: Updated note in requested format
    """
    async with _get_client() as client:
        try:
            note_data = {}
            if params.title:
                note_data["title"] = params.title
            if params.details is not None:
                note_data["details"] = params.details
            if params.todo_date:
                note_data["todo_date"] = params.todo_date
            if params.course_id is not None:
                note_data["course_id"] = params.course_id
            
            response = await client.put(
                f"/api/v1/planner_notes/{params.note_id}",
                json=note_data
            )
            response.raise_for_status()
            data = response.json()
            return _format_response(
                data,
                params.response_format,
                f"Updated Planner Note {params.note_id}"
            )
        except Exception as e:
            return _handle_canvas_error(e, f"updating planner note {params.note_id}")


@mcp.tool(
    name="canvas_delete_planner_note",
    annotations={
        "title": "Delete Planner Note",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def canvas_delete_planner_note(params: PlannerNoteIdInput) -> str:
    """
    Delete a planner note.
    
    Permanently deletes a planner note.
    
    Args:
        params (PlannerNoteIdInput): Note ID to delete
        
    Returns:
        str: Confirmation message
    """
    async with _get_client() as client:
        try:
            response = await client.delete(f"/api/v1/planner_notes/{params.note_id}")
            response.raise_for_status()
            # Canvas returns 200 OK with empty body on successful delete
            if params.response_format == ResponseFormat.JSON:
                return json.dumps({"status": "deleted", "note_id": params.note_id})
            return f"✅ Successfully deleted planner note {params.note_id}"
        except Exception as e:
            return _handle_canvas_error(e, f"deleting planner note {params.note_id}")


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Run the MCP server."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Canvas LMS MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport type: stdio (default, for Claude/Cline/Cursor), streamable-http (MCP Inspector), sse (Cursor SSE)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/SSE transport (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for HTTP/SSE transport (default: localhost)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        # Standard stdio transport for most MCP clients
        mcp.run()
    elif args.transport == "sse":
        # SSE transport for enhanced Cursor compatibility
        if args.port != 8000:
            os.environ["PORT"] = str(args.port)
        if args.host != "localhost":
            os.environ["HOST"] = args.host
        # Log to stderr to avoid interfering with SSE protocol
        print(f"Starting Canvas MCP Server with SSE transport on {args.host}:{args.port}", file=sys.stderr)
        print(f"SSE endpoint: http://{args.host}:{args.port}/sse", file=sys.stderr)
        mcp.run(transport="sse")
    else:
        # Streamable HTTP transport for MCP Inspector debugging
        if args.port != 8000:
            os.environ["PORT"] = str(args.port)
        if args.host != "localhost":
            os.environ["HOST"] = args.host
        print(f"Starting Canvas MCP Server with HTTP transport on {args.host}:{args.port}", file=sys.stderr)
        print(f"MCP endpoint: http://{args.host}:{args.port}/mcp", file=sys.stderr)
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
