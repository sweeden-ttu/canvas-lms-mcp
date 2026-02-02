#!/bin/bash
# Setup cron job to fetch repository every other day for both users
# Run with appropriate permissions (sudo)

set -e

DOUG_HOME="/home/sdw3098"
CASEY_HOME="/home/jck1278"
REPO_NAME="canvas-lms-mcp"

echo "Setting up fetch cron jobs..."

# Create fetch script for Doug
cat > /tmp/doug-fetch-repo.sh << 'EOF'
#!/bin/bash
cd /home/sdw3098/canvas-lms-mcp 2>/dev/null || exit 0
git fetch --all --prune 2>&1 | logger -t canvas-lms-mcp-fetch-doug
EOF

# Create fetch script for Casey
cat > /tmp/casey-fetch-repo.sh << 'EOF'
#!/bin/bash
cd /home/jck1278/canvas-lms-mcp 2>/dev/null || exit 0
git fetch --all --prune 2>&1 | logger -t canvas-lms-mcp-fetch-casey
EOF

# Make scripts executable
chmod +x /tmp/doug-fetch-repo.sh
chmod +x /tmp/casey-fetch-repo.sh

# Move scripts to user directories if possible
if [ -d "$DOUG_HOME" ]; then
    cp /tmp/doug-fetch-repo.sh "$DOUG_HOME/fetch-canvas-repo.sh" 2>/dev/null || true
    chmod +x "$DOUG_HOME/fetch-canvas-repo.sh" 2>/dev/null || true
fi

if [ -d "$CASEY_HOME" ]; then
    cp /tmp/casey-fetch-repo.sh "$CASEY_HOME/fetch-canvas-repo.sh" 2>/dev/null || true
    chmod +x "$CASEY_HOME/fetch-canvas-repo.sh" 2>/dev/null || true
fi

# Create cron entries (every other day = every 2 days)
# Cron format: minute hour day-of-month month day-of-week
# Every other day: 0 2 */2 * * (at 2 AM every 2 days)

CRON_DOUG="0 2 */2 * * /home/sdw3098/fetch-canvas-repo.sh"
CRON_CASEY="0 2 */2 * * /home/jck1278/fetch-canvas-repo.sh"

echo ""
echo "Cron job entries to add (run as root or respective users):"
echo ""
echo "For Doug (sdw3098):"
echo "$CRON_DOUG"
echo ""
echo "For Casey (jck1278):"
echo "$CRON_CASEY"
echo ""
echo "To add these cron jobs, run:"
echo "  sudo -u sdw3098 crontab -e  # Then add: $CRON_DOUG"
echo "  sudo -u jck1278 crontab -e  # Then add: $CRON_CASEY"
echo ""
echo "Or add to system crontab:"
echo "  sudo crontab -e  # Then add both lines"
echo ""