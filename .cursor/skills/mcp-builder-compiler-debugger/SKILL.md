---
name: mcp-builder-compiler-debugger
description: Build, test, and debug MCP (Model Context Protocol) servers using FastMCP. Use when creating MCP servers, testing endpoints, debugging connection issues, integrating with Claude Desktop, or working with MCP Inspector. Covers project setup, tool implementation patterns, error handling, testing workflows, and debugging techniques.
---

# MCP Builder, Compiler, Debugger

Guide for building, testing, and debugging MCP servers using FastMCP.

## Quick Start

**Initialize project:**
```bash
mkdir mcp-server-name && cd mcp-server-name
uv init --name mcp-server-name --python 3.10+
uv add "mcp[cli]>=1.2.0" httpx python-dotenv pydantic
uv add --dev pytest pytest-asyncio pytest-cov mypy ruff
```

**Minimal server template:**
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

### Standard Project Structure

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

**Key points:**
- Fail fast if `.env` is missing
- Use Pydantic for validation
- Load config at module level for server initialization

### Tool Implementation Workflow

**Step 1: Define Input Model**
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

**Step 2: Load Configuration and Implement Tool Function**

**At module level (before tool definitions):**
```python
from config import load_env_config, get_api_headers

# Load configuration at startup
_config = load_env_config()
```

**Tool function implementation:**
```python
import json
import httpx
from config import get_api_headers

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
    async with httpx.AsyncClient(
        base_url=_config.base_url,
        headers=get_api_headers(_config.api_token),
        timeout=30.0
    ) as client:
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
        except Exception as e:
            return handle_error(e, "fetching resource")
```

**Alternative: Use helper function for client creation:**
```python
def _get_client() -> httpx.AsyncClient:
    """Create an HTTP client with authentication."""
    return httpx.AsyncClient(
        base_url=_config.base_url,
        headers=get_api_headers(_config.api_token),
        timeout=30.0,
    )

async def get_resource(params: CourseInput) -> str:
    """Get resource description."""
    async with _get_client() as client:
        # ... rest of implementation
```

**Step 3: Error Handling Pattern**
```python
def handle_error(e: Exception, context: str = "") -> str:
    prefix = f"Error {context}: " if context else "Error: "
    
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return f"{prefix}Invalid API token. Check .env file."
        elif status == 403:
            return f"{prefix}Permission denied."
        elif status == 404:
            return f"{prefix}Resource not found."
        elif status == 429:
            return f"{prefix}Rate limited. Wait before retrying."
        return f"{prefix}HTTP {status}: {e.response.reason_phrase}"
    
    return f"{prefix}{type(e).__name__}: {str(e)}"
```

**Implementation checklist:**
- [ ] Define Pydantic input model with Field descriptions
- [ ] Use async httpx.AsyncClient for API calls
- [ ] Set appropriate tool annotations
- [ ] Handle errors with actionable messages
- [ ] Support both JSON and Markdown output formats
- [ ] Include docstring describing tool purpose

## Testing Workflow

### Test-First Development Pattern

**1. Write live API tests before implementing tools:**
```python
import pytest
import httpx
from config import load_config

@pytest.fixture(scope="module")
def api_client():
    config = load_config()
    client = httpx.Client(
        base_url=config.base_url,
        headers={"Authorization": f"Bearer {config.api_token}"},
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

**2. Run tests:**
```bash
uv run pytest tests/ -v                    # All tests
uv run pytest tests/test_live.py -v        # Specific file
uv run pytest tests/ --cov=. --cov-report=html  # With coverage
```

**3. Generate specification from verified endpoints:**
```python
# generate_spec.py
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

**4. Only implement tools for verified endpoints**

### Code Quality Checks

```bash
uv run mypy server.py          # Type checking
uv run ruff check .            # Linting
uv run ruff format .           # Formatting
```

## Debugging Workflow

### Step-by-Step Debugging Process

**1. Test server locally:**
```bash
uv run python server.py
# Should start without errors (stdio transport)
```

**2. Use MCP Inspector for interactive testing:**
```bash
# Terminal 1: Start server with HTTP transport
uv run python server.py --transport streamable-http --port 8000

# Terminal 2: Launch Inspector
npx @modelcontextprotocol/inspector
```
Open `http://localhost:8000/mcp` in Inspector to test tools interactively.

**3. Verify configuration:**
```python
from config import load_config
config = load_config()
print(f"Base URL: {config.base_url}")
print(f"Token: {'*' * 8}...{config.api_token[-4:]}")
```

**4. Check logs:**
- Claude Desktop: `~/Library/Logs/Claude/mcp*.log` (macOS)
- Server stderr output (stdio transport)

### Common Issues & Solutions

**Server not appearing in Claude Desktop:**
- [ ] Validate JSON syntax in `claude_desktop_config.json`
- [ ] Use absolute paths (not relative)
- [ ] Restart Claude Desktop completely (Cmd+Q on macOS, not just close window)
- [ ] Check MCP logs for startup errors

**401 Unauthorized:**
- Verify API token in `.env` is valid
- Token may have expired - regenerate in service settings
- Check token hasn't been revoked

**403 Forbidden:**
- Expected for some endpoints with limited permissions
- Verify account has required role/permissions
- Some endpoints may be instructor-only

**Connection Refused:**
- Ensure server process is running
- Verify path in config is correct and executable
- Check Python/uv are in PATH

**Rate Limiting (429):**
- Implement exponential backoff in error handler
- Wait before retrying (check `Retry-After` header)
- Monitor rate limit headers: `X-Rate-Limit-Remaining`

### Transport Options

**stdio (default for Claude Desktop):**
```python
if __name__ == "__main__":
    mcp.run()  # Uses stdio by default
```

**streamable-http (for Inspector debugging):**
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

**Configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):**
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

**Integration checklist:**
- [ ] Use absolute paths (required)
- [ ] Verify JSON syntax is valid
- [ ] Restart Claude Desktop completely (Cmd+Q on macOS)
- [ ] Check logs: `~/Library/Logs/Claude/mcp*.log`
- [ ] Test tools appear in Claude's tool list

## Best Practices Checklist

- [ ] **Test-first:** Verify endpoints via live API tests before implementing tools
- [ ] **Type safety:** Use Pydantic BaseModel for all tool inputs with Field descriptions
- [ ] **Error handling:** Provide actionable error messages with context
- [ ] **Security:** Never commit `.env` files (add to `.gitignore`)
- [ ] **Documentation:** Include clear docstrings describing tool purpose and parameters
- [ ] **Tool annotations:** Set appropriate hints (see patterns below)
- [ ] **Pagination:** Handle pagination for list endpoints (check Link headers)
- [ ] **Rate limiting:** Implement exponential backoff for rate-limited APIs
- [ ] **Response formats:** Support both JSON and Markdown output formats
- [ ] **Async/await:** Use async httpx.AsyncClient for all HTTP requests

## Tool Annotation Patterns

**Read-only tools (GET operations):**
```python
annotations={
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}
```

**Create tools (POST operations):**
```python
annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,  # Creates new resource each time
    "openWorldHint": True,
}
```

**Update tools (PUT/PATCH operations):**
```python
annotations={
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": True,  # Same update = same result
    "openWorldHint": True,
}
```

**Delete tools (DELETE operations):**
```python
annotations={
    "readOnlyHint": False,
    "destructiveHint": True,  # Permanently deletes
    "idempotentHint": True,  # Deleting twice = same result
    "openWorldHint": True,
}
```
