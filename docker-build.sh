#!/bin/bash
# Build script for Canvas LMS MCP Docker container

set -e

echo "Building Canvas LMS MCP Docker image..."

# Build the image
docker build -t canvas-lms-mcp:latest .

echo "Build complete!"
echo ""
echo "To run the container:"
echo "  docker run -it --rm -v \$(pwd)/.env:/app/.env:ro canvas-lms-mcp:latest"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up"
