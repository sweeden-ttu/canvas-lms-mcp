# Canvas LMS MCP Server

A **Model Context Protocol (MCP)** server that provides Claude with secure, verified access to your Canvas LMS account at Texas Tech University.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol developed by Anthropic that allows AI assistants like Claude to securely interact with external services. Think of it as "USB-C for AI" — a standardized way to connect Claude to your data and tools.

This MCP server enables Claude to:
- 📚 List your enrolled courses
- 📝 Retrieve assignments and due dates
- 📊 Check your grades
- 📢 Read course announcements
- 🗓️ View upcoming events and to-do items
- 💬 Access discussion topics

## Features

- **Test-First Design**: Only exposes endpoints verified to work with your Canvas account
- **Secure**: API tokens stored in `.env`, never committed to version control
- **Type-Safe**: Full Pydantic validation on all inputs
- **Actionable Errors**: Clear error messages guide you to solutions
- **Dual Output**: Supports both human-readable Markdown and machine-readable JSON

---

## Prerequisites

- **Python 3.10+**
- **uv** (recommended) or pip
- **Canvas API Token** from your institution
- **Claude Desktop** or **Claude Code** (for MCP integration)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/canvas-lms-mcp.git
cd canvas-lms-mcp
```

### 2. Install Dependencies

Using `uv` (recommended):
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync
```

Using `pip`:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Setup worktree (skills and agents)

To run UV-based setup and discover all Cursor skills and agents in this repo:

```bash
./setup-worktree.sh
```

Or run only the discovery step (after `uv sync`):

```bash
uv run setup-worktree
# or: uv run python scripts/setup_worktree.py
```

This syncs dependencies, ensures `.env` from `.env.example` if missing, and reports all `.cursor/skills`, `.cursor/agents`, and `agents/` Python agents.

### 4. Configure Credentials

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your Canvas credentials:
```env
CANVAS_API_TOKEN=your_actual_token_here
CANVAS_BASE_URL=https://texastech.instructure.com
```

#### How to Get Your Canvas API Token

1. Log in to Canvas at https://texastech.instructure.com
2. Click your profile picture → **Settings**
3. Scroll to **Approved Integrations**
4. Click **+ New Access Token**
5. Enter a purpose (e.g., "Claude MCP Server")
6. Click **Generate Token**
7. **Copy the token immediately** — you won't see it again!

### 5. Configure Test Hints (Optional)

For targeted testing, create `test_hints.json`:
```json
{
  "valid_course_ids": [58606, 53482, 51243],
  "test_assignment_id": null,
  "test_module_id": null
}
```

---

## Running the Server

### Option A: Direct Execution (Testing)

```bash
# Using uv
uv run python server.py

# Using activated virtualenv
python server.py
```

### Option B: With MCP Inspector (Debugging)

The MCP Inspector provides a web UI to test your server:

```bash
# Start the server with streamable HTTP for inspector
uv run python server.py --transport streamable-http --port 8000

# In another terminal
npx @modelcontextprotocol/inspector
```

Then open `http://localhost:8000/mcp` in the Inspector.

### Option C: Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

> **Important**: Use absolute paths. On Windows, use forward slashes or escaped backslashes.

Restart Claude Desktop completely (Cmd+Q on macOS, not just close the window).

### Option D: Kiro CLI Integration

For integration with Kiro CLI, add the server to your MCP configuration:

1. **Install the Canvas LMS MCP Server:**
   ```bash
   git clone https://github.com/sweeden-ttu/canvas-lms-mcp.git
   cd canvas-lms-mcp
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

2. **Configure your Canvas API token:**
   ```bash
   cp .env.example .env
   # Edit .env with your Canvas API token and base URL
   ```

3. **Add to Kiro CLI MCP configuration** (`~/.kiro/mcp_servers.json`):
   ```json
   {
     "mcpServers": {
       "canvas-lms": {
         "command": "/ABSOLUTE/PATH/TO/canvas-lms-mcp/venv/bin/python",
         "args": ["/ABSOLUTE/PATH/TO/canvas-lms-mcp/server.py"],
         "env": {}
       }
     }
   }
   ```

4. **Restart Kiro CLI** to load the new MCP server.

> **Important**: Use absolute paths and ensure the `.env` file contains your Canvas API token.

### Option E: Claude Code Integration

```bash
# Add the MCP server
claude mcp add canvas_mcp -- uv --directory /path/to/canvas-lms-mcp run python server.py

# Verify it's connected
claude mcp list

# Start Claude Code
claude
```

---

## Available Tools

Once connected, Claude can use these tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `canvas_get_profile` | Get your Canvas user profile | None |
| `canvas_list_courses` | List your enrolled courses | `enrollment_state` (optional) |
| `canvas_get_todo` | Get your to-do items | `per_page` (optional) |
| `canvas_get_upcoming_events` | Get upcoming calendar events | `per_page` (optional) |
| `canvas_get_assignments` | Get assignments for a course | `course_id` (required), `per_page` |
| `canvas_get_modules` | Get modules for a course | `course_id` (required), `per_page` |
| `canvas_get_announcements` | Get announcements for courses | `course_ids` (required) |
| `canvas_get_discussions` | Get discussion topics | `course_id` (required), `per_page` |
| `canvas_get_grades` | Get your grades/enrollment | `course_id` (required) |

---

## Example Usage with Claude

Once configured, you can ask Claude things like:

> "What assignments are due this week in my Canvas courses?"

> "Show me the announcements from all my classes"

> "What's my current grade in course 58606?"

> "List all my active courses"

> "What do I have on my to-do list?"

---

## Querying Endpoints Manually

For debugging or scripting, you can query the Canvas API directly:

```bash
# Set your token
export CANVAS_API_TOKEN="your_token_here"
export CANVAS_URL="https://texastech.instructure.com"

# Get your profile
curl -H "Authorization: Bearer $CANVAS_API_TOKEN" \
     "$CANVAS_URL/api/v1/users/self/profile"

# List courses
curl -H "Authorization: Bearer $CANVAS_API_TOKEN" \
     "$CANVAS_URL/api/v1/courses?enrollment_state=active&per_page=50"

# Get assignments for a course
curl -H "Authorization: Bearer $CANVAS_API_TOKEN" \
     "$CANVAS_URL/api/v1/courses/58606/assignments?per_page=50"
```

---

## Project Structure

```
canvas-lms-mcp/
├── .env                      # Your credentials (never commit!)
├── .env.example              # Template for credentials
├── .gitignore                # Git ignore rules
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # This file
├── CLAUDE.md                 # Instructions for Claude Code
├── config.py                 # Configuration loader
├── server.py                 # MCP Server implementation
├── generate_spec.py          # Specification generator
├── test_hints.json           # Test configuration hints
├── verified_canvas_spec.json # Generated API specification
└── tests/
    └── test_canvas_live.py   # Live API tests
```

---

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. **Check JSON syntax**: Validate `claude_desktop_config.json` in a JSON linter
2. **Use absolute paths**: Relative paths won't work
3. **Restart completely**: Cmd+Q (macOS) or right-click system tray → Quit (Windows)
4. **Check logs**: `~/Library/Logs/Claude/mcp*.log` (macOS)

### 401 Unauthorized Errors

- Your API token may be invalid or expired
- Regenerate a new token in Canvas Settings → Approved Integrations

### 403 Forbidden Errors

- Some endpoints require instructor/TA privileges
- The `/files` endpoint typically requires elevated permissions
- This is normal for student accounts

### Rate Limiting (429)

- Canvas has rate limits (typically 700 requests per 10 minutes)
- The server implements exponential backoff automatically
- If you hit limits, wait a few minutes before retrying

### Connection Refused

- Ensure the server is running
- Check that the path in the config is correct
- Verify Python and uv are in your PATH

---

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html
```

### Generating the Specification

After running live tests:

```bash
uv run python generate_spec.py
```

This creates `verified_canvas_spec.json` documenting which endpoints work.

### Code Quality

```bash
# Type checking
uv run mypy server.py

# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

---

## Security Considerations

- **Never commit `.env`** — it contains your API token
- **Token scope**: Canvas tokens have full access to your account; treat them like passwords
- **Local only**: This server runs locally via stdio; it doesn't expose an HTTP endpoint by default
- **No persistence**: The server doesn't store any Canvas data

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`uv run pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Anthropic](https://anthropic.com) for creating the Model Context Protocol
- [Canvas LMS](https://www.instructure.com/canvas) for their comprehensive REST API
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for the Python MCP SDK
- [Amazon Web Services](https://aws.amazon.com) for Kiro CLI integration support

---

## Integration Documentation

- **Kiro CLI Integration**: See installation instructions above for Kiro CLI setup
- **Claude Desktop Integration**: See [CLAUDE.md](CLAUDE.md) for detailed Claude Desktop setup
- **Amazon Q CLI Integration**: See [QCHAT_INTEGRATION.md](QCHAT_INTEGRATION.md) for Q CLI setup

## Links

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Canvas REST API Documentation](https://canvas.instructure.com/doc/api/index.html)
- [Claude Desktop](https://claude.ai/download)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
