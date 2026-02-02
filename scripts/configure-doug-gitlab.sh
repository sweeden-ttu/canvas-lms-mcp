#!/bin/bash
# Configure Doug's repository to use GitLab remote
# Run as user sdw3098 or with sudo -u sdw3098

set -e

DOUG_HOME="/home/sdw3098"
REPO_NAME="canvas-lms-mcp"
REPO_PATH="$DOUG_HOME/$REPO_NAME"
GITLAB_URL="https://gitlab.com/ttu6332505/29rc2.9.3/canvas-lms-mcp.git"

echo "Configuring Doug's repository for GitLab..."

if [ ! -d "$REPO_PATH" ]; then
    echo "Error: Repository not found at $REPO_PATH"
    exit 1
fi

cd "$REPO_PATH"

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Determine default branch (main or master)
if git show-ref --verify --quiet refs/heads/main; then
    DEFAULT_BRANCH="main"
elif git show-ref --verify --quiet refs/heads/master; then
    DEFAULT_BRANCH="master"
else
    DEFAULT_BRANCH="$CURRENT_BRANCH"
fi

echo "Default branch: $DEFAULT_BRANCH"

# Remove existing origin if it exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "Removing existing origin remote..."
    git remote remove origin
fi

# Add GitLab as origin
echo "Adding GitLab remote..."
git remote add origin "$GITLAB_URL"

# Rename branch to main if needed
if [ "$CURRENT_BRANCH" != "main" ] && [ "$DEFAULT_BRANCH" = "main" ]; then
    echo "Renaming branch to main..."
    git branch -M main
    CURRENT_BRANCH="main"
fi

# Push to GitLab
echo "Pushing to GitLab..."
git push -uf origin "$CURRENT_BRANCH"

echo "GitLab configuration complete!"
echo "Repository is now configured with GitLab remote: $GITLAB_URL"