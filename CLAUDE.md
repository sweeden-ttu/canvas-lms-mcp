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

### 🔲 MILESTONE 5: Extended Endpoint Implementation (IN PROGRESS)

This milestone adds support for module file downloads, personal calendar management, and planner functionality.

#### 5.1 Files/Modules Tools (Read-only for Students)

| Tool Name | Endpoint | Description | Status |
|-----------|----------|-------------|--------|
| `canvas_list_module_items` | `GET /api/v1/courses/:course_id/modules/:module_id/items` | List items within a specific module | 🔲 TODO |
| `canvas_get_course_file` | `GET /api/v1/courses/:course_id/files/:file_id` | Get file metadata for a course file | 🔲 TODO |
| `canvas_get_file_download_url` | `GET /api/v1/files/:file_id/public_url` | Get temporary public download URL | 🔲 TODO |

**Implementation Notes:**
- Module items can be of type `"File"` and include a `content_id` referencing the file
- The `File` object includes a `url` field with direct download URL
- A `verifier` parameter is often included for authentication
- Students can only download files they have permission to view (published files in unlocked modules)
- The existing `canvas_get_modules` tool returns module list; these new tools drill deeper

#### 5.2 Calendar Tools (Personal Calendar Only)

| Tool Name | Endpoint | HTTP Method | Description | Status |
|-----------|----------|-------------|-------------|--------|
| `canvas_list_calendar_events` | `/api/v1/calendar_events` | GET | List calendar events for current user | 🔲 TODO |
| `canvas_create_calendar_event` | `/api/v1/calendar_events` | POST | Create personal calendar event | 🔲 TODO |
| `canvas_update_calendar_event` | `/api/v1/calendar_events/:id` | PUT | Update own calendar event | 🔲 TODO |
| `canvas_delete_calendar_event` | `/api/v1/calendar_events/:id` | DELETE | Delete own calendar event | 🔲 TODO |

**Implementation Notes:**
- For creating events, use `context_code=user_<self>` to target personal calendar
- Students can ONLY modify their own personal calendar events
- Students CANNOT add/modify events on course calendars (requires instructor permission)
- Students CANNOT modify assignment due dates (managed via Assignments API)
- Events include: title, description, start_at, end_at, location_name
- Support recurring events via `rrule` parameter

**Example Create Event Request:**
```python
POST /api/v1/calendar_events
{
    "calendar_event": {
        "context_code": "user_self",
        "title": "Study Session",
        "start_at": "2025-01-15T14:00:00Z",
        "end_at": "2025-01-15T16:00:00Z",
        "location_name": "Library Room 201"
    }
}
```

#### 5.3 Planner Tools (Full CRUD for Students)

| Tool Name | Endpoint | HTTP Method | Description | Status |
|-----------|----------|-------------|-------------|--------|
| `canvas_list_planner_items` | `/api/v1/planner/items` | GET | List planner items (assignments, events, notes) | 🔲 TODO |
| `canvas_list_planner_notes` | `/api/v1/planner_notes` | GET | List planner notes | 🔲 TODO |
| `canvas_create_planner_note` | `/api/v1/planner_notes` | POST | Create a planner note | 🔲 TODO |
| `canvas_update_planner_note` | `/api/v1/planner_notes/:id` | PUT | Update a planner note | 🔲 TODO |
| `canvas_delete_planner_note` | `/api/v1/planner_notes/:id` | DELETE | Delete a planner note | 🔲 TODO |

**Implementation Notes:**
- Planner Notes are personal reminders that appear on the student planner
- PlannerNote fields: `title`, `details`, `todo_date`, `course_id` (optional), `linked_object_type`, `linked_object_id`
- Planner Items aggregate assignments, calendar events, and notes in one view
- Filter planner items by date range using `start_date` and `end_date` parameters

**Example Planner Note:**
```json
{
    "id": 234,
    "title": "Bring books tomorrow",
    "details": "I need to bring books for my biology course",
    "user_id": 1578941,
    "workflow_state": "active",
    "course_id": 1578941,
    "todo_date": "2025-01-09T10:12:00Z"
}
```

---

## 📋 IMPLEMENTATION TODO LIST

### Phase 1: API Testing (Postman)
Before implementing, test each endpoint in Postman to verify access:

- [ ] Test `GET /api/v1/courses/:course_id/modules/:module_id/items` with valid module_id
- [ ] Test `GET /api/v1/courses/:course_id/files/:file_id` with valid file_id  
- [ ] Test `GET /api/v1/files/:file_id/public_url` with valid file_id
- [ ] Test `GET /api/v1/calendar_events` (list own events)
- [ ] Test `POST /api/v1/calendar_events` (create personal event)
- [ ] Test `PUT /api/v1/calendar_events/:id` (update own event)
- [ ] Test `DELETE /api/v1/calendar_events/:id` (delete own event)
- [ ] Test `GET /api/v1/planner/items` (list planner items)
- [ ] Test `GET /api/v1/planner_notes` (list notes)
- [ ] Test `POST /api/v1/planner_notes` (create note)
- [ ] Test `PUT /api/v1/planner_notes/:id` (update note)
- [ ] Test `DELETE /api/v1/planner_notes/:id` (delete note)

### Phase 2: Update test_hints.json
- [ ] Add `valid_module_id` for module items testing
- [ ] Add `valid_file_id` for file testing (find a published file in a module)
- [ ] Add `test_calendar_event_id` after creating a test event
- [ ] Add `test_planner_note_id` after creating a test note

### Phase 3: Update generate_spec.py
- [ ] Add new endpoints to the specification generator
- [ ] Run generator to create updated `verified_canvas_spec.json`

### Phase 4: Implement Pydantic Input Models

```python
# Add to server.py

class ModuleItemsInput(BaseModel):
    """Input for listing module items."""
    course_id: int = Field(..., description="Canvas course ID")
    module_id: int = Field(..., description="Canvas module ID")
    per_page: int = Field(default=50, ge=1, le=100)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

class FileInput(BaseModel):
    """Input for file operations."""
    file_id: int = Field(..., description="Canvas file ID")
    course_id: Optional[int] = Field(None, description="Course ID (optional, for context)")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

class CalendarEventInput(BaseModel):
    """Input for creating/updating calendar events."""
    title: str = Field(..., description="Event title")
    start_at: str = Field(..., description="Start datetime (ISO 8601)")
    end_at: Optional[str] = Field(None, description="End datetime (ISO 8601)")
    description: Optional[str] = Field(None, description="Event description")
    location_name: Optional[str] = Field(None, description="Location name")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

class CalendarEventIdInput(BaseModel):
    """Input for calendar event operations requiring an ID."""
    event_id: int = Field(..., description="Calendar event ID")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

class PlannerNoteInput(BaseModel):
    """Input for creating/updating planner notes."""
    title: str = Field(..., description="Note title")
    details: Optional[str] = Field(None, description="Note details/description")
    todo_date: str = Field(..., description="Date to show on planner (ISO 8601)")
    course_id: Optional[int] = Field(None, description="Associated course ID (optional)")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

class PlannerNoteIdInput(BaseModel):
    """Input for planner note operations requiring an ID."""
    note_id: int = Field(..., description="Planner note ID")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
```

### Phase 5: Implement MCP Tools

#### Files/Modules Tools
- [ ] Implement `canvas_list_module_items(course_id, module_id)`
- [ ] Implement `canvas_get_course_file(course_id, file_id)`
- [ ] Implement `canvas_get_file_download_url(file_id)`

#### Calendar Tools  
- [ ] Implement `canvas_list_calendar_events(start_date?, end_date?, context_codes?)`
- [ ] Implement `canvas_create_calendar_event(title, start_at, end_at?, description?, location?)`
- [ ] Implement `canvas_update_calendar_event(event_id, title?, start_at?, end_at?, description?, location?)`
- [ ] Implement `canvas_delete_calendar_event(event_id)`

#### Planner Tools
- [ ] Implement `canvas_list_planner_items(start_date?, end_date?)`
- [ ] Implement `canvas_list_planner_notes()`
- [ ] Implement `canvas_create_planner_note(title, todo_date, details?, course_id?)`
- [ ] Implement `canvas_update_planner_note(note_id, title?, details?, todo_date?, course_id?)`
- [ ] Implement `canvas_delete_planner_note(note_id)`

### Phase 6: Add Tool Annotations

```python
# Read-only tools
@mcp.tool(annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True
})

# Create tools (not idempotent)
@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,  # Creates new resource each time
    "openWorldHint": True
})

# Update tools (idempotent)
@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": True,  # Same update = same result
    "openWorldHint": True
})

# Delete tools (destructive)
@mcp.tool(annotations={
    "readOnlyHint": False,
    "destructiveHint": True,  # Permanently deletes
    "idempotentHint": True,   # Deleting twice = same result
    "openWorldHint": True
})
```

### Phase 7: Testing & Documentation
- [ ] Test all new tools via MCP Inspector
- [ ] Update README.md with new tool documentation
- [ ] Update verified_canvas_spec.json with new endpoints
- [ ] Test integration with Claude Desktop

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

## MCP submodules

Additional MCP servers can be added as git submodules under `mcp/`. Run `./scripts/add_mcp_submodule.sh` (or `uv run python scripts/add_mcp_submodule.py`) and enter a GitHub repo URL when prompted. The script adds the submodule under `mcp/<repo-name>`, runs `git submodule update --init --recursive`, updates `.cursor/mcp.json` for Cursor project settings, and integrates the server into `docs/MCP_SUBMODULES.md` and `.cursor/worktrees.json`. Enter `q` to quit the loop.

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
├── mcp/                      # Git submodules for other MCP servers
│   └── README.md
├── .cursor/
│   └── mcp.json              # Cursor MCP project settings (updated by add_mcp_submodule)
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
        "readOnlyHint": False,      # Does not modify data
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
