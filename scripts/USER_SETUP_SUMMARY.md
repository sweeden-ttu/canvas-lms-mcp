# User Repository Setup Summary

## Completed Setup

### Doug (sdw3098)
- ✅ Repository cloned to `/home/sdw3098/canvas-lms-mcp`
- ✅ GitLab remote configured: `git@gitlab.com:ttu6332505/29rc2.9.3/canvas-lms-mcp.git`
- ✅ Branch set to `main`
- ✅ Fetch cron job configured: Runs every other day at 2 AM (`0 2 */2 * *`)
- ⚠️ GitLab push pending: Requires SSH key to be added to GitLab account

### Casey (jck1278)
- ✅ Repository cloned to `/home/jck1278/canvas-lms-mcp`
- ✅ GitHub remote configured: `https://github.com/sweeden-ttu/canvas-lms-mcp.git`
- ✅ Branch: `main`
- ⚠️ Fetch cron job: Cannot be set up due to PAM configuration restrictions

## Next Steps

### For Doug's GitLab Push

Doug needs to add an SSH public key to GitLab:

1. **Generate SSH key** (if not exists):
   ```bash
   sudo -u sdw3098 ssh-keygen -t ed25519 -C "sdw3098@ttu.edu" -f /home/sdw3098/.ssh/id_ed25519_gitlab
   ```

2. **Display public key**:
   ```bash
   sudo -u sdw3098 cat /home/sdw3098/.ssh/id_ed25519_gitlab.pub
   ```

3. **Add to GitLab**:
   - Go to https://gitlab.com/profile/keys
   - Click "Add new key"
   - Paste the public key
   - Save

4. **Push to GitLab**:
   ```bash
   sudo -u sdw3098 bash -c 'cd /home/sdw3098/canvas-lms-mcp && git push -uf origin main'
   ```

### For Casey's Cron Job

Casey's cron access is restricted. Alternative options:

1. **System-wide cron** (requires root):
   ```bash
   sudo crontab -e
   # Add: 0 2 */2 * * /home/jck1278/fetch-canvas-repo.sh
   ```

2. **Manual fetch script**:
   Casey can run `/home/jck1278/fetch-canvas-repo.sh` manually when needed

## Fetch Scripts

Both users have fetch scripts:
- `/home/sdw3098/fetch-canvas-repo.sh` - Fetches Doug's repository
- `/home/jck1278/fetch-canvas-repo.sh` - Fetches Casey's repository

These scripts:
- Fetch all branches and prune deleted ones
- Log output to system logger
- Exit gracefully if repository doesn't exist

## Repository Locations

- **Doug**: `/home/sdw3098/canvas-lms-mcp`
  - Remote: GitLab (`git@gitlab.com:ttu6332505/29rc2.9.3/canvas-lms-mcp.git`)
  - Branch: `main`

- **Casey**: `/home/jck1278/canvas-lms-mcp`
  - Remote: GitHub (`https://github.com/sweeden-ttu/canvas-lms-mcp.git`)
  - Branch: `main`

## Cron Schedule

- **Frequency**: Every other day (every 2 days)
- **Time**: 2:00 AM
- **Format**: `0 2 */2 * *`
- **Status**: 
  - Doug: ✅ Configured
  - Casey: ❌ Blocked by PAM (needs system cron or manual execution)