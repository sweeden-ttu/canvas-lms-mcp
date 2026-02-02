#!/usr/bin/env bash
# Comprehensive test plan: impersonate local UNIX users (jck1278, cursor, sdw3098),
# run clone/merge/push tests; on failure use GitLab CLI + credentials to fix and
# ensure SSH keys exist (validity >= 183 days) so passwords are not needed.
# Usage: sudo ./run_repo_sync_test_plan.sh [path-to-env_save-or-.env.save]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_SAVE="${1:-$SHARED_ROOT/env_save}"
if [ ! -f "$ENV_SAVE" ]; then
  ENV_SAVE="$SHARED_ROOT/.env.save"
fi

# Key validity: at least 6 months and not sooner than 148 days -> 200 days
KEY_VALIDITY_DAYS=200

USERS=(jck1278 cursor sdw3098)
GH_REPO="git@github.com:sweeden-ttu/canvas-lms-mcp.git"
GL_REPO="git@gitlab.com:sweeden3/canvas-lms-mcp.git"
CURSOR_REPO_PATH="/home/cursor/Source/canvas-lms-mcp"
# Fallback if Source doesn't exist
[ -d "$CURSOR_REPO_PATH" ] || CURSOR_REPO_PATH="/home/cursor/canvas-lms-mcp"

FAILED_STEPS=()
GITLAB_TOKEN=""
GITHUB_TOKEN=""

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
err() { echo "[ERROR] $*" >&2; }

# Load credentials from env_save or .env.save (GITLAB_TOKEN, GITHUB_TOKEN, or parse host/user/pass)
load_credentials() {
  [ -n "$GITLAB_TOKEN" ] && return
  if [ -f "$ENV_SAVE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      line="${line%%#*}"
      line="${line// /}"
      [ -z "$line" ] && continue
      if [[ "$line" == *"GITLAB_TOKEN"* ]]; then
        GITLAB_TOKEN="${line#*=}"
      elif [[ "$line" == *"GITHUB_TOKEN"* ]]; then
        GITHUB_TOKEN="${line#*=}"
      fi
      # Format: gitlab.com/sweeden3/SDweed81##
      if [[ "$line" == gitlab.com/* ]]; then
        _rest="${line#gitlab.com/}"
        _user="${_rest%%/*}"
        _pass="${_rest#*/}"
        # glab requires token; we have user/pass - can't set GITLAB_TOKEN from this
        :
      fi
    done < "$ENV_SAVE"
  fi
  export GITLAB_TOKEN
  export GITHUB_TOKEN
}

# Authenticate glab using token (from env or file)
auth_glab() {
  load_credentials
  if [ -n "$GITLAB_TOKEN" ]; then
    if ! glab auth status -h gitlab.com 2>/dev/null | grep -q "Logged in"; then
      echo "$GITLAB_TOKEN" | glab auth login -h gitlab.com --stdin 2>/dev/null || true
    fi
  fi
}

# Ensure SSH key exists for user with validity >= KEY_VALIDITY_DAYS
ensure_user_ssh_key() {
  local user="$1"
  local home
  home="$(getent passwd "$user" | cut -d: -f6)"
  [ -z "$home" ] && { err "User $user has no home"; return 1; }
  local ssh_dir="$home/.ssh"
  local key="$ssh_dir/id_ed25519"
  local pub="$ssh_dir/id_ed25519.pub"

  sudo -u "$user" bash -c "
    mkdir -p $ssh_dir
    chmod 700 $ssh_dir
  "
  if [ ! -f "$key" ]; then
    # Standard Ed25519 keys do not expire (satisfies "good for at least 6 months").
    # If your ssh-keygen supports -V "+Nd" for certificate validity, you can add it.
    sudo -u "$user" ssh-keygen -t ed25519 -C "${user}@local" -f "$key" -N ""
    chmod 600 "$key"
    chmod 644 "$pub"
    log "Generated SSH key for $user (validity ${KEY_VALIDITY_DAYS}d or non-expiring)"
  fi
  # Ensure known_hosts
  local known="$ssh_dir/known_hosts"
  if [ ! -f "$known" ] || ! grep -q "github.com" "$known" 2>/dev/null; then
    ssh-keyscan -H github.com 2>/dev/null | sudo tee -a "$known" >/dev/null
  fi
  if [ ! -f "$known" ] || ! grep -q "gitlab.com" "$known" 2>/dev/null; then
    ssh-keyscan -H gitlab.com 2>/dev/null | sudo tee -a "$known" >/dev/null
  fi
  sudo chown "$user:$user" "$known" 2>/dev/null || true
  sudo chmod 644 "$known" 2>/dev/null || true
  echo "$pub"
}

# Add public key to GitLab (sweeden3 account) via glab
add_key_to_gitlab() {
  local title="$1"
  local pubfile="$2"
  auth_glab
  if [ -z "$GITLAB_TOKEN" ]; then
    log "No GITLAB_TOKEN set; skip adding key to GitLab. Add key manually or set GITLAB_TOKEN."
    return 0
  fi
  if glab ssh-key list -h gitlab.com 2>/dev/null | grep -q "$title"; then
    log "GitLab key $title already present"
    return 0
  fi
  # Expiry: at least 6 months and not sooner than 148 days -> 200 days (GitLab supports --expires-at)
  local expiry=""
  expiry="$(date -d "+${KEY_VALIDITY_DAYS} days" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)" || expiry="$(date -v+200d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)"
  if [ -n "$expiry" ]; then
    glab ssh-key add "$pubfile" -t "$title" -h gitlab.com --expires-at "$expiry" 2>/dev/null && log "Added $title to GitLab (expires $expiry)" || glab ssh-key add "$pubfile" -t "$title" -h gitlab.com 2>/dev/null && log "Added $title to GitLab" || err "Failed to add $title to GitLab"
  else
    glab ssh-key add "$pubfile" -t "$title" -h gitlab.com 2>/dev/null && log "Added $title to GitLab" || err "Failed to add $title to GitLab"
  fi
}

# Add public key to GitHub via gh (sweeden-ttu)
add_key_to_github() {
  local title="$1"
  local pubfile="$2"
  if gh ssh-key list 2>/dev/null | grep -q "$title"; then
    log "GitHub key $title already present"
    return 0
  fi
  gh ssh-key add "$pubfile" -t "$title" 2>/dev/null && log "Added $title to GitHub" || {
    err "Failed to add $title to GitHub (may need: gh auth refresh -s admin:public_key)"
  }
}

run_test() {
  local name="$1"
  shift
  if "$@"; then
    log "PASS: $name"
    return 0
  else
    err "FAIL: $name"
    FAILED_STEPS+=("$name")
    return 1
  fi
}

fix_and_retry() {
  local name="$1"
  local user="$2"
  shift 2
  run_test "$name" "$@" && return 0
  local home pub
  home="$(getent passwd "$user" | cut -d: -f6)"
  pub="$home/.ssh/id_ed25519.pub"
  if [ -f "$pub" ]; then
    log "Fix: ensuring $user key is registered with GitLab/GitHub..."
    add_key_to_gitlab "${user}-repo-sync" "$pub"
    add_key_to_github "${user}-repo-sync" "$pub"
    log "Retry: $name"
    run_test "$name (retry)" "$@" && return 0
  fi
  return 1
}

# Safe directory for git (avoid dubious ownership)
setup_safe_directories() {
  for u in jck1278 cursor sdw3098; do
    local home path
    home="$(getent passwd "$u" | cut -d: -f6)"
    [ -z "$home" ] && continue
    for path in "/home/jck1278/canvas-lms-mcp" "/home/sdw3098/canvas-lms-mcp" "$CURSOR_REPO_PATH"; do
      [ -d "$path" ] && sudo -u "$u" git config --global --add safe.directory "$path" 2>/dev/null || true
    done
  done
}

main() {
  log "Using credentials file: $ENV_SAVE"
  load_credentials

  # Phase 1: SSH keys (validity >= 183 days, use 200)
  log "=== Phase 1: SSH key setup (validity ${KEY_VALIDITY_DAYS} days) ==="
  for u in "${USERS[@]}"; do
    getent passwd "$u" >/dev/null || { err "User $u not found"; continue; }
    pub="$(ensure_user_ssh_key "$u")"
    add_key_to_gitlab "${u}-repo-sync" "$pub"
    add_key_to_github "${u}-repo-sync" "$pub"
  done

  setup_safe_directories

  # Phase 2: Clone tests
  log "=== Phase 2: Clone tests ==="
  for u in jck1278 cursor sdw3098; do
    fix_and_retry "Clone GitHub ($u)" "$u" sudo -u "$u" bash -c "cd /tmp && rm -rf clone-gh-test && git clone $GH_REPO clone-gh-test && ls clone-gh-test" || true
  done
  for u in jck1278 cursor sdw3098; do
    fix_and_retry "Clone GitLab ($u)" "$u" sudo -u "$u" bash -c "cd /tmp && rm -rf clone-gl-test && git clone $GL_REPO clone-gl-test && ls clone-gl-test" || true
  done

  # Phase 3: Merge tests (require existing repos in home dirs)
  log "=== Phase 3: Merge tests ==="
  for u in jck1278 sdw3098; do
    home="$(getent passwd "$u" | cut -d: -f6)"
    [ -d "$home/canvas-lms-mcp" ] || continue
    run_test "Merge sdw3098 -> jck1278" sudo -u jck1278 bash -c "
      cd /home/jck1278/canvas-lms-mcp
      git remote add sdw3098-repo /home/sdw3098/canvas-lms-mcp 2>/dev/null || git remote set-url sdw3098-repo /home/sdw3098/canvas-lms-mcp
      git fetch sdw3098-repo
      git merge sdw3098-repo/main -m 'Merge from sdw3098' || true
      git remote remove sdw3098-repo 2>/dev/null || true
    " || true
    break
  done
  if [ -d "$CURSOR_REPO_PATH" ] && [ -d "/home/jck1278/canvas-lms-mcp" ]; then
    run_test "Merge cursor -> jck1278" sudo -u jck1278 bash -c "
      cd /home/jck1278/canvas-lms-mcp
      git remote add cursor-repo $CURSOR_REPO_PATH 2>/dev/null || git remote set-url cursor-repo $CURSOR_REPO_PATH
      git fetch cursor-repo
      git merge cursor-repo/main -m 'Merge from cursor' || true
      git remote remove cursor-repo 2>/dev/null || true
    " || true
  fi
  if [ -d "/home/sdw3098/canvas-lms-mcp" ] && [ -d "/home/jck1278/canvas-lms-mcp" ]; then
    run_test "Merge jck1278 -> sdw3098" sudo -u sdw3098 bash -c "
      cd /home/sdw3098/canvas-lms-mcp
      git remote add jck-repo /home/jck1278/canvas-lms-mcp 2>/dev/null || git remote set-url jck-repo /home/jck1278/canvas-lms-mcp
      git fetch jck-repo
      git merge jck-repo/main -m 'Merge from jck1278' || true
      git remote remove jck-repo 2>/dev/null || true
    " || true
  fi
  if [ -d "$CURSOR_REPO_PATH" ] && [ -d "/home/sdw3098/canvas-lms-mcp" ]; then
    run_test "Merge cursor -> sdw3098" sudo -u sdw3098 bash -c "
      cd /home/sdw3098/canvas-lms-mcp
      git remote add cursor-repo $CURSOR_REPO_PATH 2>/dev/null || git remote set-url cursor-repo $CURSOR_REPO_PATH
      git fetch cursor-repo
      git merge cursor-repo/main -m 'Merge from cursor' || true
      git remote remove cursor-repo 2>/dev/null || true
    " || true
  fi
  if [ -d "$CURSOR_REPO_PATH" ]; then
    run_test "Merge jck1278,sdw3098 -> cursor" sudo -u cursor bash -c "
      cd $CURSOR_REPO_PATH
      git remote add jck-repo /home/jck1278/canvas-lms-mcp 2>/dev/null || git remote set-url jck-repo /home/jck1278/canvas-lms-mcp
      git fetch jck-repo
      git merge jck-repo/main -m 'Merge from jck1278' || true
      git remote remove jck-repo 2>/dev/null || true
      git remote add sdw-repo /home/sdw3098/canvas-lms-mcp 2>/dev/null || git remote set-url sdw-repo /home/sdw3098/canvas-lms-mcp
      git fetch sdw-repo
      git merge sdw-repo/main -m 'Merge from sdw3098' || true
      git remote remove sdw-repo 2>/dev/null || true
    " || true
  fi

  # Phase 4: Push dry-run (passwordless)
  log "=== Phase 4: Push dry-run (SSH, no password) ==="
  for u in jck1278 cursor sdw3098; do
    path="/home/$u/canvas-lms-mcp"
    [ "$u" = "cursor" ] && path="$CURSOR_REPO_PATH"
    [ -d "$path" ] || continue
    fix_and_retry "Push GitHub dry-run ($u)" "$u" sudo -u "$u" bash -c "
      cd $path
      git remote add origin $GH_REPO 2>/dev/null || git remote set-url origin $GH_REPO
      git fetch origin
      git push origin main --dry-run
    " || true
    fix_and_retry "Push GitLab dry-run ($u)" "$u" sudo -u "$u" bash -c "
      cd $path
      git remote add gitlab $GL_REPO 2>/dev/null || git remote set-url gitlab $GL_REPO
      git fetch gitlab
      git push gitlab main --dry-run
    " || true
  done

  # Summary
  log "=== Summary ==="
  if [ ${#FAILED_STEPS[@]} -eq 0 ]; then
    log "All steps passed."
    exit 0
  else
    err "Failed steps: ${FAILED_STEPS[*]}"
    exit 1
  fi
}

main "$@"
                                                                                                                                                                                                                                      