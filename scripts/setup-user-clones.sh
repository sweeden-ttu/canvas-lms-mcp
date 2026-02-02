#!/bin/bash
# Setup repository clones for users Doug and Casey
# Run with appropriate permissions (sudo or as respective users)

set -e

REPO_URL="git@github.com:sweeden-ttu/canvas-lms-mcp.git"
DOUG_HOME="/home/sdw3098"
CASEY_HOME="/home/jck1278"
REPO_NAME="canvas-lms-mcp"

echo "Setting up repository clones for Doug and Casey..."

# Setup SSH known_hosts for GitHub
setup_ssh() {
    local user_home=$1
    local ssh_dir="$user_home/.ssh"
    
    if [ ! -d "$ssh_dir" ]; then
        mkdir -p "$ssh_dir"
        chmod 700 "$ssh_dir"
    fi
    
    if [ ! -f "$ssh_dir/known_hosts" ] || ! grep -q "github.com" "$ssh_dir/known_hosts" 2>/dev/null; then
        echo "Adding GitHub to known_hosts for $user_home..."
        ssh-keyscan github.com >> "$ssh_dir/known_hosts" 2>&1 || true
        chmod 644 "$ssh_dir/known_hosts"
    fi
}

# Clone for Doug
if [ -d "$DOUG_HOME" ]; then
    echo "Cloning repository for Doug ($DOUG_HOME)..."
    setup_ssh "$DOUG_HOME"
    if [ -d "$DOUG_HOME/$REPO_NAME" ]; then
        echo "Repository already exists for Doug, skipping clone"
    else
        cd "$DOUG_HOME"
        git clone "$REPO_URL" "$REPO_NAME" || {
            echo "Warning: Clone failed, may need SSH keys configured"
        }
        echo "Repository cloned for Doug"
    fi
else
    echo "Warning: Doug's home directory ($DOUG_HOME) does not exist"
fi

# Clone for Casey
if [ -d "$CASEY_HOME" ]; then
    echo "Cloning repository for Casey ($CASEY_HOME)..."
    setup_ssh "$CASEY_HOME"
    if [ -d "$CASEY_HOME/$REPO_NAME" ]; then
        echo "Repository already exists for Casey, skipping clone"
    else
        cd "$CASEY_HOME"
        git clone "$REPO_URL" "$REPO_NAME" || {
            echo "Warning: Clone failed, may need SSH keys configured"
        }
        echo "Repository cloned for Casey"
    fi
else
    echo "Warning: Casey's home directory ($CASEY_HOME) does not exist"
fi

echo "Clone setup complete!"