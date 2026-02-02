#!/bin/bash
# Clone repository for Doug (sdw3098)
# Run as: sudo -u sdw3098 bash clone-for-doug.sh

set -e

REPO_URL="git@github.com:sweeden-ttu/canvas-lms-mcp.git"
REPO_NAME="canvas-lms-mcp"
USER_HOME="/home/sdw3098"

cd "$USER_HOME"

# Setup SSH known_hosts
if [ ! -d "$USER_HOME/.ssh" ]; then
    mkdir -p "$USER_HOME/.ssh"
    chmod 700 "$USER_HOME/.ssh"
fi

if [ ! -f "$USER_HOME/.ssh/known_hosts" ] || ! grep -q "github.com" "$USER_HOME/.ssh/known_hosts" 2>/dev/null; then
    ssh-keyscan github.com >> "$USER_HOME/.ssh/known_hosts" 2>&1 || true
    chmod 644 "$USER_HOME/.ssh/known_hosts"
fi

# Clone repository
if [ -d "$USER_HOME/$REPO_NAME" ]; then
    echo "Repository already exists at $USER_HOME/$REPO_NAME"
else
    echo "Cloning repository for Doug..."
    git clone "$REPO_URL" "$REPO_NAME" || {
        echo "SSH clone failed. Trying HTTPS..."
        git clone "https://github.com/sweeden-ttu/canvas-lms-mcp.git" "$REPO_NAME"
    }
    echo "Repository cloned successfully"
fi