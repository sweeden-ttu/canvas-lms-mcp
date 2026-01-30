# Docker Setup for Canvas LMS MCP Server

This document describes how to build and run the Canvas LMS MCP server using Docker with an RPM-based Linux distribution (Fedora). The image runs **RPM/Python/AutoGen/LangSmith/CanvasMCP agents** and can **instantiate two worktrees**: Canvas LMS content retrieval and Trustworthy AI presentation-generator.

## Two Worktrees and Orchestration

The default command runs **orchestration** (not the MCP server):

1. **Worktree 1 – Canvas LMS content**: Builds a skeleton and table of contents from the course syllabus; fills sections using Canvas MCP and subagents.
2. **Worktree 2 – Trustworthy AI presentation**: Builds a skeleton and ToC for the presentation topic; fills sections using the presentation-generator and subagents.
3. **CI/CD plan**: Generates Mermaid + Markdown documentation aligning the Dockerfile with GitHub and GitLab workflows; uses hypothesis_generator and cross-repository evidence_evaluator; updates schema files, skeleton, and ToC for the presentation-generator and BayesianOrchestrator.

To run the **MCP server** instead, pass `server` (or use `http` for HTTP transport). See [Run the Container](#run-the-container).

## Prerequisites

- Docker installed and running
- Docker Compose (optional, for easier management)
- `.env` file with your Canvas API credentials

## Quick Start

### Build the Image

```bash
# Using the build script
./docker-build.sh

# Or manually
docker build -t canvas-lms-mcp:latest .
```

### Run the Container

**Default: orchestration (two worktrees + CI/CD plan)**  
```bash
docker run -it --rm canvas-lms-mcp:latest
# or explicitly:
docker run -it --rm canvas-lms-mcp:latest orchestrate
```

**MCP server (stdio or HTTP)**  
```bash
# Stdio transport (for Claude Desktop)
docker run -it --rm \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$(pwd)/test_hints.json:/app/test_hints.json:ro" \
  canvas-lms-mcp:latest server

# HTTP transport (for MCP Inspector)
docker run -it --rm -p 8000:8000 \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$(pwd)/test_hints.json:/app/test_hints.json:ro" \
  canvas-lms-mcp:latest http
```

**Option 1: Using the run script**
```bash
# Stdio transport (for Claude Desktop)
./docker-run.sh

# HTTP transport (for MCP Inspector debugging)
./docker-run.sh http
```

**Option 2: Using docker run directly**
```bash
# Stdio transport
docker run -it --rm \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$(pwd)/test_hints.json:/app/test_hints.json:ro" \
  canvas-lms-mcp:latest server

# HTTP transport (for debugging)
docker run -it --rm -p 8000:8000 \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$(pwd)/test_hints.json:/app/test_hints.json:ro" \
  canvas-lms-mcp:latest http
```

**Option 3: Using docker-compose**
```bash
# Start with stdio transport
docker-compose up

# Start with HTTP transport (edit docker-compose.yml to uncomment the command line)
docker-compose up
```

## Base Image

The Dockerfile uses **Fedora 39** as the base image, which provides:
- Python 3.12 (meets the >=3.10 requirement)
- RPM package manager (dnf)
- Modern toolchain and libraries

### Alternative Base Images

If you prefer a different RPM-based distribution, you can modify the Dockerfile:

**Rocky Linux 9:**
```dockerfile
FROM rockylinux:9
# Note: Rocky Linux 9 comes with Python 3.9, so you'll need to install Python 3.11+
# from EPEL or build from source
```

**AlmaLinux 9:**
```dockerfile
FROM almalinux:9
# Similar to Rocky Linux - may need Python 3.11+ installation
```

**CentOS Stream 9:**
```dockerfile
FROM quay.io/centos/centos:stream9
# Similar considerations as Rocky/AlmaLinux
```

## Image Details

- **Base OS:** Fedora 39 (RPM-based)
- **Python Version:** 3.12
- **Package Manager:** uv (installed via official installer)
- **User:** Runs as non-root user (`appuser`) for security
- **Working Directory:** `/app`
- **Port:** 8000 (for HTTP transport)

## Environment Variables

The container expects the following environment variables (typically from `.env` file):

- `CANVAS_API_TOKEN` - Your Canvas API token
- `CANVAS_BASE_URL` - Canvas instance URL (default: https://texastech.instructure.com)

## Volume Mounts

The container mounts:
- `.env` file (read-only) - Contains API credentials
- `test_hints.json` (read-only) - Optional test configuration

## Building for Production

For production deployments, consider:

1. **Multi-stage build** to reduce image size
2. **Security scanning** with tools like `trivy` or `snyk`
3. **Non-root user** (already implemented)
4. **Health checks** for container orchestration

Example production build:
```bash
docker build --no-cache -t canvas-lms-mcp:v1.0.0 .
```

## Troubleshooting

### Python Version Issues

If you encounter Python version issues:
```bash
# Check Python version in container
docker run --rm canvas-lms-mcp:latest python3 --version
```

### Missing Dependencies

If you need additional system packages, modify the Dockerfile:
```dockerfile
RUN dnf -y install \
    python3 \
    python3-devel \
    # ... other packages ...
    your-additional-package
```

### Permission Issues

If you encounter permission issues with mounted volumes:
```bash
# Ensure .env file has correct permissions
chmod 644 .env
```

### Network Issues

For HTTP transport, ensure port 8000 is accessible:
```bash
# Check if port is in use
netstat -tuln | grep 8000
# Or
ss -tuln | grep 8000
```

## Integration with Claude Desktop

To use the containerized MCP server with Claude Desktop, you'll need to configure it to run the Docker container. Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "canvas_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/absolute/path/to/.env:/app/.env:ro",
        "canvas-lms-mcp:latest"
      ]
    }
  }
}
```

## Development

For development, you may want to mount the source code:

```bash
docker run -it --rm \
  -v "$(pwd):/app" \
  -v "$(pwd)/.env:/app/.env:ro" \
  canvas-lms-mcp:latest \
  bash
```

This allows you to edit files and test changes without rebuilding the image.

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t canvas-lms-mcp:${{ github.sha }} .
      - name: Test image
        run: docker run --rm canvas-lms-mcp:${{ github.sha }} python3 --version
```
