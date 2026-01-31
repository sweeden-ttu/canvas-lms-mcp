# Canvas LMS MCP Server

A **Model Context Protocol (MCP)** server that provides secure, verified access to your Canvas LMS account at Texas Tech University.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol developed by Anthropic that allows AI assistants to securely interact with external services. Think of it as "USB-C for AI" — a standardized way to connect AI tools to your data.

This MCP server enables AI assistants to:
- 📚 List your enrolled courses
- 📝 Retrieve assignments and due dates
- 📊 Check your grades
- 📢 Read course announcements
- 🗓️ View and manage your calendar
- 💬 Access discussion topics
- 📔 Manage planner notes

## Supported MCP Clients

| Client | Status | Setup Guide |
|--------|--------|-------------|
| **Claude Desktop** | ✅ Fully Supported | See below or [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| **Claude Code** | ✅ Fully Supported | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| **Cline (VS Code)** | ✅ Supported | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| **Cursor** | ✅ Supported | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| **Gemini CLI** | ✅ Supported | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| **VS Code Native** | ✅ Supported | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |

> **📖 For detailed setup instructions for each client, see [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md)**

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

### 6. MCP submodules (optional)

Additional MCP servers can be added as **git submodules** under the `mcp/` folder. From the repo root, run:

```bash
./scripts/add_mcp_submodule.sh
# or: uv run python scripts/add_mcp_submodule.py
```

The script will prompt for a GitHub source URL, then:

1. Add the repo as a submodule under `mcp/<repo-name>`
2. Clone and sync submodules recursively
3. Register the MCP server in Cursor project settings (`.cursor/mcp.json`)
4. Integrate the server into `docs/MCP_SUBMODULES.md` and `.cursor/worktrees.json`

Enter `q` to quit the loop. After cloning the main repo, run `git submodule update --init --recursive` to fetch all submodules. See `mcp/README.md` for details.

### 7. Evaluate MCP command usefulness (optional)

Once an MCP server is added and its commands have been inferred and documented (e.g. in `.cursor/mcp.json` and `docs/MCP_SUBMODULES.md`), evaluate the usefulness of each command for the following tasks:

- **Canvas content**: Retrieving files from Canvas; reviewing and indexing existing course content; extracting topics, lectures, and examples.
- **Documentation and examples**: Retrieving and crawling documentation and examples online that can enhance existing skills, agents, and features.
- **Presentations and orchestration**: Enhancing the Reveal.js presentation or improving the BayesianOrchestrator with new skills and subagent tasks.
- **Cross-MCP and schema**: Leveraging other MCP servers in the worktree and workflow; designing improved schema files; and updating templates to use new MCP server functionality.

Use this evaluation to prioritize which commands to wire into worktrees, skills, and agents, and to keep schema and templates aligned with available MCP tools.

### 8. No synthetic, mock, or dummy data; review-changes step (required)

Evidence evaluators, examples, templates, and presentations must **never** use "synthetic", "mock", or "dummy" data. Whenever such fake data would be introduced:

1. **Hypothesis**: State a testable hypothesis for what real data or behavior is needed.
2. **Planned experiment**: Define a concrete experiment (e.g. live API call, real course content, real documentation fetch) to obtain or validate real data.
3. **Evaluate evidence and results**: Run the experiment, collect evidence, and update beliefs (e.g. via BayesianOrchestrator); use the resulting real data in examples, templates, and presentations.

**Review-changes step**: Every change set must include a **review-changes** step that:

- Evaluates the step-by-step instructions that were followed
- Performs a peer review of the changes (e.g. via cs-peer-reviewer-trustworthy-ai or equivalent)
- Attempts to reproduce the results (run the same steps and verify outcomes)
- **Accepts** the premise (and keeps the change) if reproduction succeeds and no synthetic/mock/dummy data was introduced, or **rejects** the premise (and reverts or rewrites) if mock/synthetic data would have been used or results cannot be reproduced

This is enforced as a project-wide rule in `.cursor/rules/`; see that rule for full wording.

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

### Option E: Cursor IDE Integration

1. **Locate Cursor MCP Configuration:**
   - Open Cursor Settings (Cmd+, on macOS)
   - Navigate to **Features** → **MCP**
   - Or manually edit the configuration file (location varies by OS)

2. **Add Canvas MCP Server:**
   - Click **"+ Add New MCP Server"** or edit the configuration file directly
   - Use the configuration from `cursor-mcp-config.json` as a reference
   - Update the path in the `args` array to match your installation:
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

3. **Set Environment Variables:**
   - Ensure your `.env` file is in the `canvas-lms-mcp` directory
   - Or set environment variables in the MCP server configuration

4. **Restart Cursor:**
   - Completely quit and restart Cursor (Cmd+Q on macOS)

### Option F: Cline (VS Code Extension) Integration

1. **Open Cline Settings:**
   - In VS Code, click the Cline icon in the sidebar
   - Navigate to **MCP Servers** tab
   - Click **"Configure"** or **"+ Add New MCP Server"**

2. **Add Canvas MCP Server:**
   - Use the configuration from `cline-mcp-config.json` as a reference
   - Update the path to match your installation:
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

3. **Set Environment Variables:**
   - Ensure your `.env` file is in the `canvas-lms-mcp` directory
   - Or configure environment variables in the MCP server settings

4. **Restart VS Code:**
   - Completely quit and restart VS Code to apply changes

---

## Multi-Client Setup

This server works with **6 different MCP clients**. Quick setup for each:

- **Claude Desktop/Code:** See options A-D above
- **Cline (VS Code):** Add to Cline MCP settings (see [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md#3-cline-vs-code-extension-setup))
- **Cursor:** Add to Cursor MCP settings or use SSE transport (see [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md#4-cursor-setup))
- **Gemini CLI:** Add to `~/.gemini/config.json` (see [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md#5-gemini-cli-setup))
- **VS Code Native:** Add to GitHub Copilot settings (see [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md#6-vs-code-native-mcp-with-github-copilot))

**📖 Complete setup instructions: [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md)**

---

## Available Tools

Once connected, your AI assistant can use these 20 Canvas tools:

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

For detailed parameter information, see the tool docstrings in [server.py](server.py).

---

## Example Usage

Once configured, you can ask your AI assistant things like:

> "What assignments are due this week in my Canvas courses?"

> "Show me the announcements from all my classes"

> "What's my current grade in course 58606?"

> "List all my active courses"

> "What do I have on my to-do list?"

> "Create a planner note to remind me to study for the exam on Friday"

> "What files are available in module 3 of my course?"

**Note:** In Cursor, you must use Composer/Agent mode (not regular chat) for MCP tools to work.

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
