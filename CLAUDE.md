# CLAUDE.md - Canvas LMS MCP Server Development Guide

## Project Overview

This project implements a **Test-Driven Discovery** approach to building an MCP (Model Context Protocol) server for Canvas LMS at Texas Tech University (`https://texastech.instructure.com`).

The core philosophy is to **verify Canvas API endpoints via live tests first**, then generate a specification of what works, and finally build an MCP server exposing only verified endpoints.

---

## Milestone Status

### ✅ MILESTONE 1: Scaffolding & Secure Configuration (COMPLETE)
- [x] Python project initialized with `uv`
- [x] Dependencies installed: `mcp[cli]`, `httpx`, `python-dotenv`, `pytest`, `pydantic`
- [x] `config.py` module created with `.env` and `test_hints.json` loading
- [x] Security: Fails immediately if `.env` is missing

### ✅ MILESTONE 2: Interactive Test Suite (COMPLETE)
Live API tests have been executed via Postman. Results summary:
- **Total Pass**: 45
- **Total Fail**: 3 (all expected 403 on `/files` endpoint)
- **Execution Time**: 7.9 seconds

**Verified Endpoints (200 OK):**
| Endpoint | Course IDs Tested | Status |
|----------|-------------------|--------|
| `GET /api/v1/users/self/profile` | N/A | ✅ Verified |
| `GET /api/v1/courses` | N/A | ✅ Verified |
| `GET /api/v1/users/self/todo` | N/A | ✅ Verified |
| `GET /api/v1/users/self/upcoming_events` | N/A | ✅ Verified |
| `GET /api/v1/courses/{id}/assignments` | 58606, 53482, 51243 | ✅ Verified |
| `GET /api/v1/courses/{id}/modules` | 58606, 53482, 51243 | ✅ Verified |
| `GET /api/v1/announcements` | 58606, 53482, 51243 | ✅ Verified |
| `GET /api/v1/courses/{id}/discussion_topics` | 58606, 53482, 51243 | ✅ Verified |
| `GET /api/v1/courses/{id}/enrollments` | 58606, 53482, 51243 | ✅ Verified |

**Failed Endpoints (403 Forbidden - Expected):**
| Endpoint | Reason |
|----------|--------|
| `GET /api/v1/courses/{id}/files` | Student accounts typically lack file access |

### ✅ MILESTONE 3: Specification Generator (COMPLETE)
- [x] Create `generate_spec.py` script
- [x] Script re-runs successful API calls to verify endpoints
- [x] Analyzes JSON response schemas
- [x] Saves `verified_canvas_spec.json` with endpoint metadata and sample schemas

**Generated Specification Results (2025-12-09):**
- Verified endpoints: 9
- Failed endpoints: 1 (files - 403 as expected)

### ✅ MILESTONE 4: MCP Server Implementation (COMPLETE)
- [x] Create `server.py` using FastMCP
- [x] Implement only verified tools:
  - [x] `canvas_get_profile()` - Get current user profile
  - [x] `canvas_list_courses()` - List enrolled courses
  - [x] `canvas_get_todo()` - Get to-do items
  - [x] `canvas_get_upcoming_events()` - Get upcoming events
  - [x] `canvas_get_assignments(course_id)` - Get course assignments
  - [x] `canvas_get_modules(course_id)` - Get course modules
  - [x] `canvas_get_announcements(course_ids)` - Get announcements
  - [x] `canvas_get_discussions(course_id)` - Get discussion topics
  - [x] `canvas_get_grades(course_id)` - Get enrollment/grades
- [x] Do NOT implement `canvas_get_files()` (verified as 403)
- [x] Add proper error handling with actionable messages
- [x] Ensure token loaded from `.env` at runtime
- [x] Support both Markdown and JSON response formats
- [x] Include tool annotations (readOnlyHint, destructiveHint, etc.)

---

## Quick Commands

```bash
# Create virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install "mcp[cli]>=1.2.0" "httpx>=0.27.0" "python-dotenv>=1.0.0" "pydantic>=2.0.0" "pytest>=8.0.0" "pytest-asyncio>=0.23.0"

# Run tests
.venv/bin/pytest tests/ -v

# Generate specification from test results
.venv/bin/python generate_spec.py

# Run the MCP server (stdio transport for local use)
.venv/bin/python server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector

# Add to Claude Code
claude mcp add canvas_mcp -- /path/to/canvas-lms-mcp/.venv/bin/python /path/to/canvas-lms-mcp/server.py
```

---

## Project Structure

```
canvas-lms-mcp/
├── .env                      # API credentials (DO NOT COMMIT)
├── .env.example              # Template for .env
├── .gitignore                # Git ignore rules
├── .venv/                    # Python virtual environment
├── pyproject.toml            # Project dependencies
├── CLAUDE.md                 # This file - Claude Code instructions
├── README.md                 # User documentation
├── config.py                 # Configuration loading
├── test_hints.json           # Course IDs and other test hints
├── verified_canvas_spec.json # Generated specification (auto-generated)
├── generate_spec.py          # Specification generator
├── server.py                 # MCP Server implementation
└── tests/
    └── test_canvas_live.py   # Live API tests
```

---

## Configuration Files

### `.env` (Required)
```env
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_BASE_URL=https://texastech.instructure.com
```

### `test_hints.json` (Optional but recommended)
```json
{
  "valid_course_ids": [58606, 53482, 51243],
  "test_assignment_id": null,
  "test_module_id": null
}
```

---

## MCP Server Design Guidelines

### Tool Naming Convention
All tools must be prefixed with `canvas_` to avoid conflicts with other MCP servers:
- ✅ `canvas_list_courses`
- ✅ `canvas_get_assignments`
- ❌ `list_courses` (too generic)
- ❌ `get_assignments` (may conflict)

### Tool Annotations
Every tool must include annotations:
```python
@mcp.tool(
    name="canvas_list_courses",
    annotations={
        "title": "List Canvas Courses",
        "readOnlyHint": True,      # Does not modify data
        "destructiveHint": False,   # No destructive operations
        "idempotentHint": True,     # Safe to repeat
        "openWorldHint": True       # Interacts with external API
    }
)
```

### Error Handling Pattern
```python
def _handle_canvas_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 401:
            return "Error: Invalid API token. Check CANVAS_API_TOKEN in .env"
        elif e.response.status_code == 403:
            return "Error: Permission denied. Your account may not have access to this resource."
        elif e.response.status_code == 404:
            return "Error: Resource not found. Verify the course_id is correct."
        elif e.response.status_code == 429:
            return "Error: Rate limited. Wait before making more requests."
    return f"Error: {type(e).__name__}: {str(e)}"
```

### Response Formats
Support both JSON and Markdown:
```python
class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"  # Human-readable
    JSON = "json"          # Machine-readable
```

---

## Critical Implementation Notes

1. **Never hardcode tokens** - Always load from `.env`
2. **Verify before implementing** - Only expose endpoints that passed tests
3. **Handle pagination** - Canvas API uses Link headers for pagination
4. **Rate limiting** - Canvas has rate limits; implement backoff
5. **stdio transport** - Use stdio for local Claude Desktop integration
6. **No stdout logging** - Use stderr for logging to avoid corrupting JSON-RPC

---

## Canvas API Reference

Base URL: `https://texastech.instructure.com/api/v1`

Authentication: Bearer token in `Authorization` header

Documentation: https://canvas.instructure.com/doc/api/index.html

### Pagination
Canvas uses Link headers:
```
Link: <https://...?page=2>; rel="next", <https://...?page=5>; rel="last"
```

### Common Parameters
- `per_page`: Items per page (max 100, default 10)
- `page`: Page number for pagination

---

## Development Workflow

1. **Make changes** to server.py or other files
2. **Test locally** with MCP Inspector: `npx @modelcontextprotocol/inspector`
3. **Restart Claude Desktop** to pick up changes
4. **Check logs**: `~/Library/Logs/Claude/mcp-server-canvas_mcp.log`

---

## Troubleshooting

### "Server not showing up in Claude"
- Check `claude_desktop_config.json` syntax
- Restart Claude Desktop completely (Cmd+Q on macOS)
- Check MCP logs for errors

### "401 Unauthorized"
- Verify CANVAS_API_TOKEN is valid
- Token may have expired - regenerate in Canvas settings

### "403 Forbidden"
- This is expected for `/files` endpoint with student accounts
- Check if you have the required role for the endpoint

### "Connection refused"
- Ensure server.py is running
- Check the path in claude_desktop_config.json is absolute
