# Amazon Q CLI Integration

This document explains how to integrate the Canvas LMS MCP Server with Amazon Q CLI (qchat).

## Prerequisites

- Amazon Q CLI installed
- Canvas API token from your institution
- Python 3.10+ with required dependencies

## Installation Steps

### 1. Clone and Install

```bash
git clone https://github.com/sweeden-ttu/canvas-lms-mcp.git
cd canvas-lms-mcp
pip install -e .
```

### 2. Configure Credentials

```bash
cp .env.example .env
# Edit .env with your Canvas API token and base URL
```

### 3. Add MCP Server to Q CLI

```bash
q mcp add --name canvas-lms --command python --args "/path/to/canvas-lms-mcp/server.py"
```

### 4. Verify Installation

```bash
q mcp list
q mcp status --name canvas-lms
```

## Usage

Once configured, the Canvas MCP server provides these tools in Q CLI chat sessions:

- `canvas_get_profile` - Get your Canvas user profile
- `canvas_list_courses` - List enrolled courses
- `canvas_get_todo` - Get to-do items
- `canvas_get_assignments` - Get course assignments
- `canvas_get_grades` - Get grades for a course
- `canvas_get_announcements` - Get course announcements
- `canvas_get_discussions` - Get discussion topics
- `canvas_get_modules` - Get course modules
- `canvas_get_upcoming_events` - Get calendar events

## Example Queries

Ask Q CLI questions like:
- "What assignments are due this week in my Canvas courses?"
- "Show me announcements from all my classes"
- "What's my current grade in course 12345?"
- "List all my active courses"

## Troubleshooting

### Server Not Loading
- Verify absolute path in MCP configuration
- Check Canvas API token is valid
- Ensure Python dependencies are installed

### 401 Unauthorized
- Regenerate Canvas API token
- Verify token has proper permissions

### 403 Forbidden
- Some endpoints require instructor privileges
- This is normal for student accounts

## Configuration Files

- **Global**: `~/.aws/amazonq/mcp.json`
- **Agent-specific**: `.amazonq/cli-agents/{agent-name}.json`

For agent-specific configuration, add to agent JSON:
```json
{
  "mcpServers": {
    "canvas-lms": {
      "command": "python",
      "args": ["/path/to/canvas-lms-mcp/server.py"]
    }
  }
}
```
