# Test Plan: Repository Sync and SSH Key Setup

This test plan verifies that local users (jck1278, cursor, sdw3098) can clone from GitHub and GitLab, merge across local repositories, and use SSH keys for passwordless push/pull operations.

## Prerequisites

- Local accounts: jck1278, cursor, sdw3098
- Repositories:
  - GitHub: https://github.com/sweeden-ttu/canvas-lms-mcp
  - GitLab: https://gitlab.com/sweeden3/canvas-lms-mcp

---

## Phase 1: SSH Key Setup (Per User)

Each user must have SSH keys configured for both GitHub and GitLab.

### 1.1 Generate SSH Key (if not present)

For each user, run as that user:

```bash
# Impersonate user (e.g., as root or via su)
sudo -u <USER> bash -c '
  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "<USER>@local" -f ~/.ssh/id_ed25519 -N ""
  fi
  chmod 600 ~/.ssh/id_ed25519
  chmod 644 ~/.ssh/id_ed25519.pub
  cat ~/.ssh/id_ed25519.pub
'
```

Repeat for: `jck1278`, `cursor`, `sdw3098`.

### 1.2 Add Public Key to GitHub

1. Log in to https://github.com as sweeden-ttu (or account with repo access)
2. Settings → SSH and GPG keys → New SSH key
3. Add each user's public key (from `~/.ssh/id_ed25519.pub`)
4. Label keys: e.g., `jck1278-billnye`, `cursor-billnye`, `sdw3098-billnye`

### 1.3 Add Public Key to GitLab

1. Log in to https://gitlab.com as sweeden3
2. Preferences → SSH Keys → Add new key
3. Add each user's public key
4. Title: e.g., `jck1278-billnye`, `cursor-billnye`, `sdw3098-billnye`

### 1.4 Verify SSH Key Connectivity

For each user:

```bash
sudo -u <USER> ssh -T git@github.com
# Expected: "Hi sweeden-ttu! You've successfully authenticated..."

sudo -u <USER> ssh -T git@gitlab.com
# Expected: "Welcome to GitLab, @sweeden3!"
```

---

## Phase 2: Clone Tests

Verify each user can clone from both remotes.

### 2.1 Clone from GitHub

| Step | User   | Command | Expected Result |
|------|--------|---------|-----------------|
| 1    | jck1278 | `sudo -u jck1278 bash -c 'cd /tmp && rm -rf clone-gh-test && git clone git@github.com:sweeden-ttu/canvas-lms-mcp.git clone-gh-test && ls clone-gh-test'` | Clone succeeds, directory populated |
| 2    | cursor | `sudo -u cursor bash -c 'cd /tmp && rm -rf clone-gh-test && git clone git@github.com:sweeden-ttu/canvas-lms-mcp.git clone-gh-test && ls clone-gh-test'` | Clone succeeds |
| 3    | sdw3098 | `sudo -u sdw3098 bash -c 'cd /tmp && rm -rf clone-gh-test && git clone git@github.com:sweeden-ttu/canvas-lms-mcp.git clone-gh-test && ls clone-gh-test'` | Clone succeeds |

### 2.2 Clone from GitLab

| Step | User   | Command | Expected Result |
|------|--------|---------|-----------------|
| 4    | jck1278 | `sudo -u jck1278 bash -c 'cd /tmp && rm -rf clone-gl-test && git clone git@gitlab.com:sweeden3/canvas-lms-mcp.git clone-gl-test && ls clone-gl-test'` | Clone succeeds |
| 5    | cursor | `sudo -u cursor bash -c 'cd /tmp && rm -rf clone-gl-test && git clone git@gitlab.com:sweeden3/canvas-lms-mcp.git clone-gl-test && ls clone-gl-test'` | Clone succeeds |
| 6    | sdw3098 | `sudo -u sdw3098 bash -c 'cd /tmp && rm -rf clone-gl-test && git clone git@gitlab.com:sweeden3/canvas-lms-mcp.git clone-gl-test && ls clone-gl-test'` | Clone succeeds |

---

## Phase 3: Cross-User Merge Tests

Verify each user can read and merge content from the others' local canvas-lms-mcp folders.

### 3.1 Permission Setup

Ensure each user's home and canvas-lms-mcp are readable by the others (or use a shared group). Options:

- Add all three users to a shared group (e.g., `canvasdev`) and set `chmod g+rx` on home and repo
- Or use `sudo -u` to impersonate and access via root

For testing with `sudo -u`, the tester has root; real-world use may need `setgid` or ACLs for peer access.

### 3.2 Merge: sdw3098 → jck1278

```bash
sudo -u jck1278 bash -c '
  cd /home/jck1278/canvas-lms-mcp
  git remote add sdw3098-repo /home/sdw3098/canvas-lms-mcp 2>/dev/null || git remote set-url sdw3098-repo /home/sdw3098/canvas-lms-mcp
  git fetch sdw3098-repo
  git merge sdw3098-repo/main -m "Merge from sdw3098" || true
  git remote remove sdw3098-repo 2>/dev/null || true
'
```

**Expected:** Fetch succeeds, merge completes (or "Already up to date").

### 3.3 Merge: cursor → jck1278

```bash
sudo -u jck1278 bash -c '
  cd /home/jck1278/canvas-lms-mcp
  git remote add cursor-repo /home/cursor/Source/canvas-lms-mcp 2>/dev/null || git remote set-url cursor-repo /home/cursor/Source/canvas-lms-mcp
  git fetch cursor-repo
  git merge cursor-repo/main -m "Merge from cursor" || true
  git remote remove cursor-repo 2>/dev/null || true
'
```

**Expected:** Fetch and merge succeed.

### 3.4 Merge: jck1278 → sdw3098

```bash
sudo -u sdw3098 bash -c '
  cd /home/sdw3098/canvas-lms-mcp
  git remote add jck-repo /home/jck1278/canvas-lms-mcp 2>/dev/null || git remote set-url jck-repo /home/jck1278/canvas-lms-mcp
  git fetch jck-repo
  git merge jck-repo/main -m "Merge from jck1278" || true
  git remote remove jck-repo 2>/dev/null || true
'
```

**Expected:** Fetch and merge succeed.

### 3.5 Merge: cursor → sdw3098

```bash
sudo -u sdw3098 bash -c '
  cd /home/sdw3098/canvas-lms-mcp
  git remote add cursor-repo /home/cursor/Source/canvas-lms-mcp 2>/dev/null || git remote set-url cursor-repo /home/cursor/Source/canvas-lms-mcp
  git fetch cursor-repo
  git merge cursor-repo/main -m "Merge from cursor" || true
  git remote remove cursor-repo 2>/dev/null || true
'
```

**Expected:** Fetch and merge succeed.

### 3.6 Merge: jck1278 → cursor, sdw3098 → cursor

```bash
sudo -u cursor bash -c '
  cd /home/cursor/Source/canvas-lms-mcp
  git remote add jck-repo /home/jck1278/canvas-lms-mcp 2>/dev/null || git remote set-url jck-repo /home/jck1278/canvas-lms-mcp
  git fetch jck-repo
  git merge jck-repo/main -m "Merge from jck1278" || true
  git remote remove jck-repo 2>/dev/null || true

  git remote add sdw-repo /home/sdw3098/canvas-lms-mcp 2>/dev/null || git remote set-url sdw-repo /home/sdw3098/canvas-lms-mcp
  git fetch sdw-repo
  git merge sdw-repo/main -m "Merge from sdw3098" || true
  git remote remove sdw-repo 2>/dev/null || true
'
```

**Expected:** Both fetches and merges succeed.

---

## Phase 4: Push/Pull Without Passwords (SSH)

Verify each user can push and pull using SSH (no password prompts).

### 4.1 Push to GitHub (per user)

```bash
# As jck1278
sudo -u jck1278 bash -c '
  cd /home/jck1278/canvas-lms-mcp
  git remote add origin git@github.com:sweeden-ttu/canvas-lms-mcp.git 2>/dev/null || git remote set-url origin git@github.com:sweeden-ttu/canvas-lms-mcp.git
  git fetch origin
  git push origin main --dry-run
'

# Repeat for cursor and sdw3098
```

**Expected:** No password prompt; `--dry-run` reports success or "Everything up-to-date".

### 4.2 Push to GitLab (per user)

```bash
sudo -u jck1278 bash -c '
  cd /home/jck1278/canvas-lms-mcp
  git remote add gitlab git@gitlab.com:sweeden3/canvas-lms-mcp.git 2>/dev/null || git remote set-url gitlab git@gitlab.com:sweeden3/canvas-lms-mcp.git
  git fetch gitlab
  git push gitlab main --dry-run
'
# Repeat for cursor and sdw3098
```

**Expected:** No password prompt.

### 4.3 Pull from Both Remotes (per user)

```bash
sudo -u <USER> bash -c '
  cd /home/<USER>/canvas-lms-mcp
  git pull origin main
  git pull gitlab main
'
```

Replace `<USER>` with jck1278, cursor, sdw3098. For cursor, use path `/home/cursor/Source/canvas-lms-mcp` if that is the canonical repo location.

**Expected:** Pulls complete without password prompts.

---

## Phase 5: Test Execution Checklist

| # | Test | jck1278 | cursor | sdw3098 | Pass/Fail |
|---|------|---------|--------|---------|-----------|
| 1 | SSH key present | | | | |
| 2 | GitHub SSH auth | | | | |
| 3 | GitLab SSH auth | | | | |
| 4 | Clone from GitHub | | | | |
| 5 | Clone from GitLab | | | | |
| 6 | Merge from sdw3098 | N/A | N/A | N/A | |
| 7 | Merge from cursor | N/A | N/A | N/A | |
| 8 | Merge from jck1278 | N/A | N/A | N/A | |
| 9 | Push to GitHub (dry-run) | | | | |
| 10 | Push to GitLab (dry-run) | | | | |
| 11 | Pull from GitHub | | | | |
| 12 | Pull from GitLab | | | | |

---

## Phase 6: Safe Directory Configuration

If Git reports "dubious ownership" when accessing another user's repo, add safe directories:

```bash
sudo git config --global --add safe.directory /home/jck1278/canvas-lms-mcp
sudo git config --global --add safe.directory /home/cursor/Source/canvas-lms-mcp
sudo git config --global --add safe.directory /home/sdw3098/canvas-lms-mcp
```

---

## Automated test script and fixing failures

A script runs this test plan as root, impersonating each user, and on failure uses the GitLab CLI and credentials to fix (e.g. register SSH keys).

1. **Run the script:**  
   `sudo bash scripts/run_repo_sync_test_plan.sh [path-to-env_save-or-.env.save]`  
   Default credentials file: `env_save` or `.env.save` in the project root.

2. **If clone/push tests fail (Permission denied / publickey):**  
   The script generates SSH keys for jck1278, cursor, and sdw3098 (non-expiring Ed25519; validity at least 6 months). To have the script register those keys with GitLab and GitHub so passwords are not needed:
   - **GitLab:** Add a Personal Access Token to your credentials file. In GitLab: **Preferences → Access Tokens**, create a token with `api` scope. Add a line to `env_save` or `.env.save`:  
     `GITLAB_TOKEN=glpat-xxxxxxxxxxxx`  
     Then re-run the script. It will use `glab` to add each user's public key to the sweeden3 account; GitLab keys are added with expiry 200 days (at least 6 months and not sooner than 148 days).
   - **GitHub:** Ensure `gh` can add SSH keys: run `gh auth refresh -s admin:public_key -h github.com` and complete the device flow. Then re-run the script so it can add each user's public key via `gh ssh-key add`.

3. **Keys and validity:**  
   - Local keys: `~/.ssh/id_ed25519` per user; standard Ed25519 keys do not expire.  
   - GitLab (when using glab): keys are added with `--expires-at` set to 200 days from now (max of 148 days and 6 months).  
   - Ensure keys do not expire sooner than 148 days and are good for at least 6 months; the script uses 200 days for GitLab key expiry.

4. **Safe directories:**  
   The script sets `safe.directory` per user for `/home/jck1278/canvas-lms-mcp`, `/home/sdw3098/canvas-lms-mcp`, and the cursor repo path to avoid "dubious ownership" when merging.

---

## Notes

- **Cursor repo path:** May be `/home/cursor/Source/canvas-lms-mcp` or `/home/cursor/canvas-lms-mcp`; adjust commands accordingly.
- **Cross-user read access:** By default, home directories are 700. For merges from peer repos, either run tests with `sudo -u` or configure group/ACL access.
- **SSH agent:** For interactive use, ensure `ssh-agent` is running and keys are added: `ssh-add ~/.ssh/id_ed25519`.
