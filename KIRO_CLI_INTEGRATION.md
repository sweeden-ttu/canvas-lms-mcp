# Kiro CLI Integration Guide

This guide shows how to integrate the Canvas LMS MCP Server with Amazon's Kiro CLI for seamless Canvas access through AI assistance.

## Prerequisites

- **Kiro CLI** installed and configured
- **Canvas API Token** from your institution
- **Python 3.10+** with virtual environment support

## Installation Steps

### 1. Clone and Install the Canvas MCP Server

```bash
# Clone the repository
git clone https://github.com/sweeden-ttu/canvas-lms-mcp.git
cd canvas-lms-mcp

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Configure Canvas Credentials

```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file with your Canvas credentials:
```env
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_BASE_URL=https://texastech.instructure.com
```

#### Getting Your Canvas API Token

1. Log in to Canvas at your institution's URL
2. Click your profile picture → **Settings**
3. Scroll to **Approved Integrations**
4. Click **+ New Access Token**
5. Enter a purpose (e.g., "Kiro CLI Integration")
6. Click **Generate Token**
7. **Copy the token immediately** — you won't see it again!

### 3. Configure Kiro CLI MCP Integration

Create or edit the MCP servers configuration file:

**File:** `~/.kiro/mcp_servers.json`

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

> **Important**: Replace `/ABSOLUTE/PATH/TO/canvas-lms-mcp` with the actual absolute path to your installation directory.

### 4. Test the Integration

Start Kiro CLI and test the Canvas integration:

```bash
kiro-cli chat
```

In the chat, you can now ask questions like:
- "What courses am I enrolled in on Canvas?"
- "Show me my upcoming assignments"
- "What announcements do I have?"
- "What's on my Canvas to-do list?"

## Available Canvas Tools

Once integrated, Kiro CLI has access to these Canvas tools:

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `canvas_get_profile` | Get your Canvas profile | "Show me my Canvas profile" |
| `canvas_list_courses` | List enrolled courses | "What courses am I taking?" |
| `canvas_get_todo` | Get to-do items | "What's on my Canvas to-do list?" |
| `canvas_get_upcoming_events` | Get upcoming events | "What events do I have coming up?" |
| `canvas_get_assignments` | Get course assignments | "Show me assignments for course 58606" |
| `canvas_get_modules` | Get course modules | "What modules are in my CS course?" |
| `canvas_get_announcements` | Get announcements | "Any new announcements?" |
| `canvas_get_discussions` | Get discussion topics | "Show me discussion topics" |
| `canvas_get_grades` | Get grades | "What are my current grades?" |

## Example Conversations

### Getting Course Information
```
> What Canvas courses am I enrolled in?

I'll check your enrolled Canvas courses.

[Canvas API call results showing your active courses]
```

### Checking Assignments
```
> Show me upcoming assignments in my computer science courses

Let me check your Canvas assignments for CS courses.

[Canvas API call results showing assignments with due dates]
```

### Managing To-Do Items
```
> What's on my Canvas to-do list?

I'll get your Canvas to-do items.

[Canvas API call results showing pending tasks and due dates]
```

## Troubleshooting

### MCP Server Not Loading

1. **Check file paths**: Ensure all paths in `mcp_servers.json` are absolute
2. **Verify Python environment**: Make sure the virtual environment is properly created
3. **Check permissions**: Ensure the Python executable and server script are executable

### Authentication Errors (401)

1. **Verify API token**: Check that your Canvas API token is correct in `.env`
2. **Token expiration**: Canvas tokens may expire; generate a new one if needed
3. **Institution URL**: Ensure `CANVAS_BASE_URL` matches your institution's Canvas URL

### Canvas API Errors (403/404)

1. **Course access**: Some courses may be archived or you may not have access
2. **Permission levels**: Some endpoints require instructor privileges
3. **Course IDs**: Verify you're using correct course IDs from `canvas_list_courses`

### Environment Variable Conflicts

If you have `CANVAS_API_TOKEN` set as an environment variable, it may override the `.env` file:

```bash
# Check for conflicting environment variables
echo $CANVAS_API_TOKEN

# Unset if needed
unset CANVAS_API_TOKEN
```

## Advanced Configuration

### Custom Course Filtering

You can create a `test_hints.json` file to specify which courses to focus on:

```json
{
  "valid_course_ids": [58606, 53482, 51243],
  "test_assignment_id": null,
  "test_module_id": null
}
```

### Logging and Debugging

To enable debug logging, modify the server startup in your MCP configuration:

```json
{
  "mcpServers": {
    "canvas-lms": {
      "command": "/ABSOLUTE/PATH/TO/canvas-lms-mcp/venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/canvas-lms-mcp/server.py", "--debug"],
      "env": {
        "PYTHONPATH": "/ABSOLUTE/PATH/TO/canvas-lms-mcp"
      }
    }
  }
}
```

## Security Considerations

- **API Token Security**: Your Canvas API token has full access to your account
- **Local Storage**: The `.env` file contains sensitive credentials
- **No Network Exposure**: The MCP server runs locally and doesn't expose network endpoints
- **Token Rotation**: Regularly rotate your Canvas API tokens for security

## Support

For issues specific to:
- **Canvas LMS MCP Server**: [GitHub Issues](https://github.com/sweeden-ttu/canvas-lms-mcp/issues)
- **Kiro CLI**: Amazon Web Services support channels
- **Canvas API**: Your institution's Canvas support

## Updates

To update the Canvas MCP Server:

```bash
cd canvas-lms-mcp
git pull origin main
source venv/bin/activate
pip install -e .
```

Restart Kiro CLI after updates to reload the MCP server.
