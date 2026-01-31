# MCP Client Compatibility Guide

This Canvas LMS MCP server is compatible with multiple MCP clients. This guide provides setup instructions for each supported client.

## Compatibility Matrix

| Client | Status | Transport | Limitations |
|--------|--------|-----------|-------------|
| **Claude Desktop** | ✅ Fully Supported | stdio | None |
| **Claude Code** | ✅ Fully Supported | stdio | None |
| **Cline (VS Code)** | ✅ Supported | stdio | Separate MCP implementation from VS Code native |
| **Cursor** | ✅ Supported | stdio, SSE | Tools only work in Agent/Composer mode, max 40 tools |
| **Gemini CLI** | ✅ Supported | stdio | Requires Gemini CLI installation |
| **VS Code (Native)** | ✅ Supported | stdio | Requires GitHub Copilot, VS Code 1.102+ |

---

## Prerequisites

Before configuring any client, ensure you have:

1. **Python 3.10+** installed
2. **Canvas API Token** from https://texastech.instructure.com
3. **Server configured** with `.env` file (see main README.md)

---

## 1. Claude Desktop Setup

### Installation

Edit your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "canvas_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/canvas-lms-mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

**Alternative (without uv):**

```json
{
  "mcpServers": {
    "canvas_mcp": {
      "command": "/ABSOLUTE/PATH/TO/canvas-lms-mcp/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/canvas-lms-mcp/server.py"
      ]
    }
  }
}
```

### Verification

1. Restart Claude Desktop completely (Cmd+Q on macOS, Quit via system tray on Windows)
2. Start a new conversation
3. Look for the 🔌 MCP icon in the bottom right
4. Test with: "What courses am I enrolled in?"

### Troubleshooting

- **Check logs:** `~/Library/Logs/Claude/mcp*.log` (macOS)
- **JSON syntax:** Validate config with https://jsonlint.com
- **Paths:** Must be absolute, not relative

---

## 2. Claude Code Setup

### Installation

```bash
# Add the MCP server
claude mcp add canvas_mcp -- uv --directory /ABSOLUTE/PATH/TO/canvas-lms-mcp run python server.py

# Or without uv:
claude mcp add canvas_mcp -- /ABSOLUTE/PATH/TO/canvas-lms-mcp/.venv/bin/python /ABSOLUTE/PATH/TO/canvas-lms-mcp/server.py

# Verify it's connected
claude mcp list
```

### Verification

```bash
# Start Claude Code
claude

# Test the connection
> What assignments do I have in Canvas?
```

### Troubleshooting

```bash
# Check MCP status
claude mcp list

# Remove and re-add if needed
claude mcp remove canvas_mcp
claude mcp add canvas_mcp -- uv --directory /path/to/canvas-lms-mcp run python server.py

# Check logs
claude mcp logs canvas_mcp
```

---

## 3. Cline (VS Code Extension) Setup

### Installation

1. Install Cline extension from VS Code Marketplace
2. Open Cline settings (Cmd/Ctrl+Shift+P → "Cline: Open Settings")
3. Navigate to **MCP Servers** section
4. Click **"Add MCP Server"**
5. Enter the following configuration:

```json
{
  "canvas_mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "/ABSOLUTE/PATH/TO/canvas-lms-mcp",
      "run",
      "python",
      "server.py"
    ]
  }
}
```

**Alternative (without uv):**

```json
{
  "canvas_mcp": {
    "command": "/ABSOLUTE/PATH/TO/canvas-lms-mcp/.venv/bin/python",
    "args": [
      "/ABSOLUTE/PATH/TO/canvas-lms-mcp/server.py"
    ]
  }
}
```

### Verification

1. Open Cline chat panel
2. Type: "List my Canvas courses"
3. Cline should invoke the `canvas_list_courses` tool

### Known Issues

- MCP hub may fail if Cline is in VS Code's secondary sidebar (move to primary)
- Environment variable inheritance issues on Windows (ensure `.env` is in server directory)
- Node.js version compatibility (use Node 18+)

### Troubleshooting

- **Check Cline logs:** View → Output → Select "Cline" from dropdown
- **Restart VS Code:** Fully quit and restart after config changes
- **Check server path:** Ensure absolute paths, no spaces without quotes

---

## 4. Cursor Setup

### Installation

#### Method 1: One-Click Setup (Recommended)

1. Open Cursor Settings (Cmd/Ctrl+,)
2. Navigate to **Features** → **Model Context Protocol (MCP)**
3. Click **"Add Server"** → **"Custom Server"**
4. Fill in:
   - **Name:** `canvas_mcp`
   - **Command:** `uv`
   - **Args:** `--directory /ABSOLUTE/PATH/TO/canvas-lms-mcp run python server.py`

#### Method 2: Manual Configuration

Edit your Cursor MCP settings file:

**macOS:** `~/Library/Application Support/Cursor/User/globalStorage/mcp/settings.json`
**Windows:** `%APPDATA%\Cursor\User\globalStorage\mcp\settings.json`
**Linux:** `~/.config/Cursor/User/globalStorage/mcp/settings.json`

```json
{
  "mcpServers": {
    "canvas_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/canvas-lms-mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

### Important Limitations

⚠️ **MCP tools only work in Cursor's Agent/Composer mode**, not in regular chat
⚠️ **Maximum 40 tools** supported (this server has 20 tools, well within limit)
⚠️ **Resources not yet supported** (this server only uses tools, so no impact)
⚠️ **May not work over SSH** or remote development environments

### Verification

1. Restart Cursor completely
2. Open **Composer** (Cmd/Ctrl+I) or **Agent mode**
3. Type: "Show me my Canvas assignments"
4. Cursor should invoke MCP tools

### Troubleshooting

- **Tools not appearing:** Make sure you're in Composer/Agent mode, not regular chat
- **Server not connecting:** Check Cursor logs (Help → Show Logs)
- **40 tool limit:** If you add other MCP servers, total tools across all servers ≤ 40

---

## 5. Gemini CLI Setup

### Installation

1. **Install Gemini CLI:**

```bash
npm install -g @google/generative-ai-cli
# or
pip install google-generativeai
```

2. **Configure API Key:**

```bash
export GEMINI_API_KEY="your_gemini_api_key"
```

3. **Create Gemini CLI config:**

Edit `~/.gemini/config.json`:

```json
{
  "mcpServers": {
    "canvas_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/canvas-lms-mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

### Verification

```bash
# Start Gemini CLI
gemini

# Test MCP connection
> What courses am I enrolled in on Canvas?
```

### Gemini-Specific Features

- Gemini CLI integrates seamlessly with FastMCP (which this server uses)
- Supports tool calling with Gemini 2.0 Flash and Gemini 2.5 Pro
- Can use Google's managed MCP servers alongside custom servers

---

## 6. VS Code Native MCP (with GitHub Copilot)

### Prerequisites

- **VS Code 1.102 or later**
- **GitHub Copilot subscription**

### Installation

1. Open VS Code Settings (JSON)
2. Add MCP server configuration:

```json
{
  "github.copilot.chat.mcpServers": {
    "canvas_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/canvas-lms-mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

### Verification

1. Reload VS Code window
2. Open GitHub Copilot Chat
3. Type: `@canvas_mcp list my courses`

---

## Environment Variables

All clients require the same `.env` configuration in your server directory:

```env
CANVAS_API_TOKEN=your_canvas_token_here
CANVAS_BASE_URL=https://texastech.instructure.com
```

### Security Notes

- ✅ `.env` stays on your local machine, never sent to MCP clients
- ✅ Clients communicate with server via stdio (local process)
- ✅ No network exposure unless you explicitly use SSE transport
- ⚠️ Treat Canvas API tokens like passwords

---

## Testing Your Setup

### Quick Test Script

Run this to verify your server works independently:

```bash
cd /path/to/canvas-lms-mcp

# Install dependencies if needed
uv sync
# or: python -m venv .venv && .venv/bin/pip install -e .

# Test server startup
uv run python server.py --transport stdio < /dev/null

# Should start without errors (Ctrl+C to stop)
```

### MCP Inspector (All Clients)

For debugging any client:

```bash
# Terminal 1: Start server with HTTP transport
cd /path/to/canvas-lms-mcp
uv run python server.py --transport streamable-http --port 8000

# Terminal 2: Start inspector
npx @modelcontextprotocol/inspector

# Open browser to http://localhost:5173
# Connect to: http://localhost:8000/mcp
# Test all 20 tools interactively
```

---

## Available Tools

All clients get access to these 20 Canvas tools:

### User Level (No Course ID Required)
- `canvas_get_profile` - Get your Canvas profile
- `canvas_list_courses` - List enrolled courses
- `canvas_get_todo` - Get to-do items
- `canvas_get_upcoming_events` - Get upcoming events

### Course Level (Require Course ID)
- `canvas_get_assignments` - Get course assignments
- `canvas_get_modules` - Get course modules
- `canvas_get_discussions` - Get discussion topics
- `canvas_get_grades` - Get enrollment/grades
- `canvas_get_announcements` - Get announcements

### Files/Modules
- `canvas_list_module_items` - List items in a module
- `canvas_get_course_file` - Get file metadata
- `canvas_get_file_download_url` - Get file download URL

### Calendar (Personal)
- `canvas_list_calendar_events` - List calendar events
- `canvas_create_calendar_event` - Create personal event
- `canvas_update_calendar_event` - Update event
- `canvas_delete_calendar_event` - Delete event

### Planner (Student Notes)
- `canvas_list_planner_items` - List planner items
- `canvas_list_planner_notes` - List planner notes
- `canvas_create_planner_note` - Create note
- `canvas_update_planner_note` - Update note
- `canvas_delete_planner_note` - Delete note

---

## Common Issues Across All Clients

### "Server not found" / "Connection failed"

1. Check paths are absolute, not relative
2. Verify Python/uv is in system PATH
3. Check `.env` file exists in server directory
4. Try running server manually to see error messages

### "401 Unauthorized"

- Canvas API token is invalid or expired
- Regenerate token at Canvas Settings → Approved Integrations

### "403 Forbidden"

- Normal for student accounts on some endpoints (e.g., bulk file listing)
- Endpoints in this server are pre-verified for student access

### "Tools not working"

- **Cursor:** Switch to Composer/Agent mode
- **Cline:** Move to primary sidebar
- **All clients:** Fully restart the client application

---

## Transport Support

| Transport | Claude Desktop | Claude Code | Cline | Cursor | Gemini CLI | VS Code Native |
|-----------|----------------|-------------|-------|--------|------------|----------------|
| **stdio** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **SSE** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **HTTP** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

This server currently supports **stdio** (standard input/output), which works with all clients.

SSE (Server-Sent Events) support can be added for enhanced Cursor compatibility (see Enhancement section below).

---

## Performance Tips

### Reduce Latency

- Use `per_page` parameters to limit results
- Cache course IDs instead of repeatedly listing courses
- Use `response_format: "json"` for programmatic parsing

### Rate Limiting

- Canvas limits: ~700 requests per 10 minutes
- Server implements automatic exponential backoff
- Space out bulk operations

---

## Enhancements for Better Compatibility

### Adding SSE Transport (Optional)

For better Cursor support, you can add SSE transport:

```python
# In server.py main()
if args.transport == "sse":
    mcp.run(transport="sse", port=args.port)
```

Then configure Cursor to use SSE:

```json
{
  "canvas_mcp": {
    "url": "http://localhost:8000/sse",
    "transport": "sse"
  }
}
```

---

## Getting Help

### Client-Specific Support

- **Claude Desktop/Code:** https://docs.anthropic.com/claude/docs
- **Cline:** https://github.com/cline/cline/issues
- **Cursor:** https://docs.cursor.com
- **Gemini CLI:** https://github.com/google-gemini/gemini-cli

### This Server

- **Issues:** https://github.com/sweeden-ttu/canvas-lms-mcp/issues
- **Canvas API Docs:** https://canvas.instructure.com/doc/api/
- **MCP Protocol:** https://modelcontextprotocol.io/

---

## References & Sources

- [VS Code MCP Support (Generally Available)](https://github.blog/changelog/2025-07-14-model-context-protocol-mcp-support-in-vs-code-is-generally-available/)
- [Cursor MCP Documentation](https://docs.cursor.com/context/model-context-protocol)
- [Google Gemini CLI + FastMCP](https://developers.googleblog.com/en/gemini-cli-fastmcp-simplifying-mcp-server-development/)
- [Google Managed MCP Servers](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
- [MCP Client Compatibility Tables](https://mcpiuse.com/)
- [Cline MCP Issues](https://github.com/cline/cline/issues/4391)

---

**Last Updated:** December 2025
**Server Version:** 0.1.0
**MCP Protocol Version:** 1.2.0+
