# MCP Servers for Course Documents, Modules, and Syllabus

This document lists MCP (Model Context Protocol) servers that can help with **extracting course documents**, **downloading course modules and files**, and **syllabus**-related workflows. Use it to find complementary servers to this Canvas LMS MCP server.

---

## This Project: canvas-lms-mcp

This repo implements a Canvas LMS MCP server with verified tools for:

- **User:** profile, courses, to-do, upcoming events
- **Course:** assignments, modules, discussions, grades, announcements
- **Modules and files:** `canvas_list_module_items`, `canvas_get_course_file`, `canvas_get_file_download_url`
- **Calendar and planner:** list/create/update/delete calendar events and planner notes

Syllabus body is not yet exposed as a dedicated tool; it is available from the Canvas API via `GET /api/v1/courses/:id?include=syllabus_body`. The [syllabus schema](../schema/syllabus_schema.json) describes the course/syllabus structure for downstream use.

---

## Other Canvas / LMS MCP Servers

These servers may offer additional capabilities (e.g. syllabus, file download, course documents). Always verify endpoints and permissions for your Canvas instance and role (student vs instructor).

| Server | Description | Course docs / modules / files / syllabus |
|--------|-------------|----------------------------------------|
| [MCP Server Directory – Canvas LMS](https://www.mcp-server-directory.com/servers/canvas-lms) | Directory entry for Canvas LMS MCP servers | Lists features: course info, syllabi, modules, assignments, quizzes, file listing, planner |
| [avarant/canvas-mcp-server](https://github.com/avarant/canvas-mcp-server) | Python, uses canvas-lms-sdk; requires Canvas URL and API key | Full Canvas integration; check repo for syllabus/module/file tools |
| [DMontgomery40/mcp-canvas-lms](https://github.com/DMontgomery40/mcp-canvas-lms) | Version 2.2, 54 tools; courses, assignments, enrollments, grades | Broad coverage; may include file and module operations |
| [plyght/canvas-mcp](https://github.com/plyght/canvas-mcp) | Canvas LMS MCP server | Check repo for course documents and file download |
| [vishalsachdev/canvas-mcp](https://github.com/vishalsachdev/canvas-mcp) | Locally runnable MCP server for Canvas LMS | Check repo for syllabus and module/file support |

---

## Using Syllabus and Course Structure

1. **Syllabus body (HTML)**  
   Request from Canvas: `GET /api/v1/courses/:id?include=syllabus_body`. The response includes a `syllabus_body` field (HTML). Use [schema/syllabus_schema.json](../schema/syllabus_schema.json) to describe the course/syllabus object.

2. **Course documents and modules**  
   - Use `canvas_list_courses` then `canvas_get_modules(course_id)` and `canvas_list_module_items(course_id, module_id)` to discover content.  
   - Use `canvas_get_course_file` and `canvas_get_file_download_url` for file metadata and download URLs (subject to Canvas permissions).

3. **Schema file for syllabus**  
   The project provides a JSON Schema for course/syllabus data: [schema/syllabus_schema.json](../schema/syllabus_schema.json). Use it to validate or document payloads when building tools that extract or display syllabus content.

---

## Adding Another MCP Server as a Submodule

To add one of the above (or any MCP server) as a submodule under `mcp/`:

```bash
./scripts/add_mcp_submodule.sh
# or: uv run python scripts/add_mcp_submodule.py
```

Enter the GitHub repo URL when prompted. The script adds the submodule, updates `.cursor/mcp.json`, and documents the server. See [mcp/README.md](../mcp/README.md) and [CLAUDE.md](../CLAUDE.md) for evaluation and wiring into skills/agents.

---

## References

- [Canvas REST API – Courses](https://canvas.instructure.com/doc/api/courses.html)
- [Canvas REST API – Syllabus (data service)](https://canvas.instructure.com/doc/api/file.data_service_canvas_syllabus.html)
- [Canvas API: syllabus_body](https://community.canvaslms.com/t5/Canvas-Developers-Group/Help-Getting-Syllabus-Through-API/m-p/515701): use `GET /api/v1/courses/:id?include=syllabus_body`
- [MCP Server Directory](https://www.mcp-server-directory.com/)
- This project: [verified_canvas_spec.json](../verified_canvas_spec.json), [schema/syllabus_schema.json](../schema/syllabus_schema.json)
