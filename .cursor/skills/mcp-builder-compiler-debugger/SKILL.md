---
name: mcp-builder-compiler-debugger
description: Build, test, and debug MCP (Model Context Protocol) servers. Use when creating MCP servers, testing endpoints, debugging connection issues, or working with FastMCP, MCP Inspector, or Claude Desktop integration.
---

# MCP Builder, Compiler, Debugger

Guide for building, testing, and debugging MCP servers using FastMCP.

## Quick Start

**Project Setup:**
```bash
# Create project structure
mkdir mcp-server-name && cd mcp-server-name
uv init --name mcp-server-name --python 3.10+

# Install MCP dependencies
uv add "mcp[cli]>=1.2.0" httpx python-dotenv pydantic

# Install dev dependencies
uv add --dev pytest pytest-asyncio pytest-cov mypy ruff
```

**Basic Server Template:**
```python
#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP(name="your_server_name")

@mcp.tool(
    name="example_tool",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def example_tool(params: dict) -> str:
    """Tool description."""
    return "result"

if __name__ == "__main__":
    mcp.run()
```

## Building MCP Servers

### Project Structure

```
mcp-server/
├── .env                    # API credentials (never commit)
├── .env.example            # Template
├── pyproject.toml          # Dependencies
├── server.py               # Main MCP server
├── config.py               # Configuration loader
├── test_hints.json         # Test configuration (optional)
└── tests/
    └── test_live.py         # Live API tests
```

### Configuration Pattern

**config.py:**
```python
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

class Config(BaseModel):
    api_token: str = Field(..., description="API token")
    base_url: str = Field(default="https://api.example.com")

def load_config() -> Config:
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("ERROR: .env file not found!", file=sys.stderr)
        sys.exit(1)
    
    load_dotenv(env_file)
    return Config(
        api_token=os.getenv("API_TOKEN", ""),
        base_url=os.getenv("BASE_URL", "https://api.example.com")
    )
```

### Tool Implementation Pattern

**Input Models:**
```python
from pydantic import BaseModel, Field
from enum import Enum

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

class CourseInput(BaseModel):
    course_id: int = Field(..., description="Course ID", gt=0)
    per_page: int = Field(default=50, ge=1, le=100)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
```

**Tool Functions:**
```python
@mcp.tool(
    name="get_resource",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def get_resource(params: CourseInput) -> str:
    """Get resource description."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"/api/v1/courses/{params.course_id}/resource",
                params={"per_page": params.per_page}
            )
            response.raise_for_status()
            data = response.json()
            
            if params.response_format == ResponseFormat.JSON:
                return json.dumps(data, indent=2)
            return format_as_markdown(data)
        except httpx.HTTPStatusError as e:
            return handle_error(e)
```

**Error Handling:**
```python
def handle_error(e: Exception, context: str = "") -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return "Error: Invalid API token. Check .env file."
        elif status == 403:
            return "Error: Permission denied."
        elif status == 404:
            return "Error: Resource not found."
        elif status == 429:
            return "Error: Rate limited. Wait before retrying."
    return f"Error: {type(e).__name__}: {str(e)}"
```

## Compiling & Testing

### Running Tests

**Live API Tests:**
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_live.py -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html
```

**Test Pattern:**
```python
import pytest
import httpx
from config import get_config, get_api_headers

@pytest.fixture(scope="module")
def api_client():
    config, _ = get_config()
    client = httpx.Client(
        base_url=config.base_url,
        headers=get_api_headers(config.api_token),
        timeout=30.0,
    )
    yield client
    client.close()

def test_endpoint(api_client):
    response = api_client.get("/api/v1/endpoint")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

### Specification Generation

Create a `generate_spec.py` script to verify endpoints and generate documentation:

```python
async def verify_endpoint(client, method, path, params=None):
    result = {
        "endpoint": path,
        "method": method,
        "verified": False,
        "status_code": None,
        "error": None,
    }
    try:
        response = await client.request(method, path, params=params)
        result["status_code"] = response.status_code
        if response.status_code == 200:
            result["verified"] = True
            result["sample_response"] = extract_schema_sample(response.json())
        else:
            result["error"] = f"HTTP {response.status_code}"
    except Exception as e:
        result["error"] = str(e)
    return result
```

Run: `uv run python generate_spec.py`

### Type Checking & Linting

```bash
# Type checking
uv run mypy server.py

# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

## Debugging

### MCP Inspector

**Start server with HTTP transport:**
```bash
uv run python server.py --transport streamable-http --port 8000
```

**In another terminal:**
```bash
npx @modelcontextprotocol/inspector
```

Open `http://localhost:8000/mcp` in Inspector to test tools interactively.

### Common Issues

**Server not appearing in Claude Desktop:**
1. Check JSON syntax in `claude_desktop_config.json`
2. Use absolute paths (not relative)
3. Restart Claude Desktop completely (Cmd+Q on macOS)
4. Check logs: `~/Library/Logs/Claude/mcp*.log` (macOS)

**401 Unauthorized:**
- Verify API token in `.env` is valid
- Token may have expired - regenerate in service settings

**403 Forbidden:**
- Expected for some endpoints with limited permissions
- Check if account has required role/permissions

**Connection Refused:**
- Ensure server is running
- Verify path in config is correct
- Check Python/uv are in PATH

**Rate Limiting (429):**
- Implement exponential backoff
- Wait before retrying
- Check rate limit headers: `X-Rate-Limit-Remaining`

### Debugging Workflow

1. **Test locally first:**
   ```bash
   uv run python server.py
   ```

2. **Use MCP Inspector for interactive testing:**
   ```bash
   uv run python server.py --transport streamable-http --port 8000
   npx @modelcontextprotocol/inspector
   ```

3. **Check logs:**
   - Claude Desktop: `~/Library/Logs/Claude/mcp*.log`
   - Server stderr output (stdio transport)

4. **Verify configuration:**
   ```python
   from config import load_config
   config = load_config()
   print(f"Base URL: {config.base_url}")
   print(f"Token: {'*' * 8}...{config.api_token[-4:]}")
   ```

### Transport Options

**stdio (default for Claude Desktop):**
```python
if __name__ == "__main__":
    mcp.run()  # Uses stdio by default
```

**streamable-http (for Inspector):**
```python
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    if args.transport == "streamable-http":
        import os
        if args.port != 8000:
            os.environ["PORT"] = str(args.port)
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
```

## Claude Desktop Integration

**Configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "server_name": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/mcp-server",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

**Important:**
- Use absolute paths
- Restart Claude Desktop completely after changes
- Check logs for errors

## Best Practices

1. **Test-first approach:** Verify endpoints work before implementing tools
2. **Type safety:** Use Pydantic for all inputs
3. **Error handling:** Provide actionable error messages
4. **Security:** Never commit `.env` files
5. **Documentation:** Include tool descriptions and parameter docs
6. **Tool annotations:** Set appropriate hints (readOnlyHint, destructiveHint, etc.)
7. **Pagination:** Handle pagination for list endpoints
8. **Rate limiting:** Implement backoff for rate-limited APIs

## Tool Annotation Guidelines

**Read-only tools:**
```python
annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}
```

**Create tools:**
```python
annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,  # Creates new resource each time
    "openWorldHint": True,
}
```

**Update tools:**
```python
annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": True,  # Same update = same result
    "openWorldHint": True,
}
```

**Delete tools:**
```python
annotations={
    "readOnlyHint": False,
    "destructiveHint": True,  # Permanently deletes
    "idempotentHint": True,  # Deleting twice = same result
    "openWorldHint": True,
}
```
