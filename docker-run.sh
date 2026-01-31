#!/bin/bash
# Run script for Canvas LMS MCP Docker container

set -e

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Please edit .env with your Canvas API token before running."
    else
        echo "Error: .env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Determine transport mode
TRANSPORT=${1:-stdio}

if [ "$TRANSPORT" = "http" ]; then
    echo "Running Canvas LMS MCP server with HTTP transport on port 8000..."
    docker run -it --rm \
        -p 8000:8000 \
        -v "$(pwd)/.env:/app/.env:ro" \
        -v "$(pwd)/test_hints.json:/app/test_hints.json:ro" \
        canvas-lms-mcp:latest http
else
    echo "Running Canvas LMS MCP server with stdio transport..."
    docker run -it --rm \
        -v "$(pwd)/.env:/app/.env:ro" \
        -v "$(pwd)/test_hints.json:/app/test_hints.json:ro" \
        canvas-lms-mcp:latest server
fi
