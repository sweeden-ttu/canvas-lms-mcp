# Canvas LMS MCP Server

A **Model Context Protocol (MCP)** server that provides secure, verified access to Canvas LMS—the open-source learning management system developed by Instructure and used by universities and schools worldwide. This server enables AI assistants like Claude to seamlessly interact with your Canvas account, allowing you to access courses, modules, assignments, grades, and more from educational institutions across the globe.

## About Canvas LMS

Canvas LMS is an open-source learning management system released under the AGPLv3 license by Instructure, Inc. It's designed for anyone interested in learning more about or using learning management systems, and is widely adopted by educational institutions worldwide. Canvas provides a comprehensive REST API that enables programmatic access to course content, student data, assignments, grades, and other educational resources.

## Capabilities & Features

This MCP server implements a **test-driven discovery approach**, exposing only Canvas API endpoints that have been verified to work with student accounts. It provides comprehensive access to your Canvas courses and academic information through the following capabilities:

### User Profile & Course Management
- **`canvas_get_profile`** - Retrieve your Canvas user profile, including name, email, login ID, and account information
- **`canvas_list_courses`** - List all enrolled courses with enrollment state filtering (active, completed, or all)
- **`canvas_get_todo`** - Get your to-do items, including pending assignments and quizzes that need attention
- **`canvas_get_upcoming_events`** - View upcoming calendar events, assignment due dates, and scheduled activities

### Course Content Access
- **`canvas_get_assignments`** - Retrieve assignments for any course, including due dates, points possible, submission status, and detailed descriptions
- **`canvas_get_modules`** - Access course module structures that organize content into units or weeks
- **`canvas_get_discussions`** - Get discussion topics and boards for courses, including message counts and participation information
- **`canvas_get_announcements`** - Fetch announcements from one or more courses, keeping you informed of instructor updates
- **`canvas_get_grades`** - Check your enrollment status and current grades for any course

### File & Module Resources
- **`canvas_list_module_items`** - List all items within a specific course module, including files, assignments, discussions, and other content
- **`canvas_get_course_file`** - Get file metadata for course files, including name, size, content-type, and download URLs
- **`canvas_get_file_download_url`** - Obtain temporary public download URLs for files you have permission to access

### Personal Calendar Management
- **`canvas_list_calendar_events`** - List your personal calendar events with optional date range filtering
- **`canvas_create_calendar_event`** - Create personal calendar events with title, description, start/end times, and location
- **`canvas_update_calendar_event`** - Update your own calendar events
- **`canvas_delete_calendar_event`** - Delete personal calendar events

### Planner & Task Management
- **`canvas_list_planner_items`** - Get aggregated planner items including assignments, calendar events, and planner notes in one unified view
- **`canvas_list_planner_notes`** - List your personal planner notes and reminders
- **`canvas_create_planner_note`** - Create planner notes with titles, details, todo dates, and optional course associations
- **`canvas_update_planner_note`** - Update existing planner notes
- **`canvas_delete_planner_note`** - Delete planner notes

## Key Features

### Test-First Design
Only endpoints verified through live API testing are exposed, ensuring reliability and compatibility with your Canvas account. The server maintains a verified specification (`verified_canvas_spec.json`) documenting which endpoints work correctly.

### Secure Authentication
- API tokens stored securely in `.env` files (never committed to version control)
- Bearer token authentication with Canvas LMS REST API
- Support for any Canvas instance worldwide (configurable base URL)

### Type-Safe Implementation
- Full Pydantic validation on all input parameters
- Comprehensive error handling with actionable error messages
- Proper HTTP status code handling (401, 403, 404, 429, 500+)

### Flexible Output Formats
- **Markdown** - Human-readable format for easy consumption
- **JSON** - Machine-readable format for programmatic use

### Global Compatibility
Works with Canvas LMS instances from any educational institution worldwide, including:
- Universities and colleges
- K-12 schools
- Training organizations
- Any institution using Canvas LMS

Simply configure your institution's Canvas base URL (e.g., `https://your-school.instructure.com`) and API token to get started.

## Use Cases

This MCP server enables AI assistants to help you with:

- **Academic Planning**: "What assignments are due this week across all my courses?"
- **Grade Tracking**: "Show me my current grades in all active courses"
- **Course Organization**: "List all modules for my Computer Science course"
- **Announcement Monitoring**: "What are the latest announcements from my instructors?"
- **Calendar Management**: "Create a study session event for tomorrow afternoon"
- **Task Management**: "Add a reminder to review my notes before the exam"
- **File Access**: "Get the download URL for the assignment file in Module 3"

## Technical Implementation

Built with:
- **Python 3.10+** with async/await support
- **FastMCP** - Fast Model Context Protocol server framework
- **httpx** - Modern async HTTP client
- **Pydantic** - Data validation and settings management
- **Test-Driven Development** - All endpoints verified before implementation

The server follows MCP protocol standards and integrates seamlessly with:
- Claude Desktop
- Claude Code
- MCP Inspector (for debugging and testing)
- Any MCP-compatible AI assistant

## Security & Privacy

- **Local Execution**: Runs entirely on your machine via stdio transport
- **No Data Persistence**: The server doesn't store any Canvas data
- **Token Security**: API tokens are stored locally in `.env` files
- **Read-Only by Default**: Most tools are read-only; write operations limited to personal calendar and planner notes
- **Permission-Aware**: Respects Canvas permission model (students can only access their own data)

## Architecture

The server implements a clean separation of concerns:
- **Configuration Layer**: Secure environment variable and test hint loading
- **API Client Layer**: Async HTTP client with proper error handling
- **Tool Layer**: MCP tools with Pydantic input validation
- **Response Formatting**: Dual-format output (Markdown/JSON) with intelligent formatting

All tools include proper MCP annotations:
- `readOnlyHint` - Indicates whether the tool modifies data
- `destructiveHint` - Marks operations that permanently delete data
- `idempotentHint` - Indicates whether repeated calls produce the same result
- `openWorldHint` - Signals interaction with external APIs

---

**Note**: This MCP server is designed for student accounts and focuses on read-only access to course content, with write access limited to personal calendar and planner functionality. Instructor-level capabilities may require additional permissions and are not currently implemented.




