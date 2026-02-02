# Sync: GITLAB_STRIP_TOKEN and repository sync

This document describes where **GITLAB_STRIP_TOKEN** is configured on each git provider (no values are stored in the repo), how to merge differences by source provider, and how to add, commit, merge, sync, pull, and push.

## GITLAB_STRIP_TOKEN by provider

| Provider | Location | Purpose |
|----------|----------|---------|
| **GitHub** | Repository → Settings → Secrets and variables → Actions → `GITLAB_STRIP_TOKEN` | Available to GitHub Actions (e.g. if a workflow pushes to GitLab). Set via: `gh secret set GITLAB_STRIP_TOKEN -R sweeden-ttu/canvas-lms-mcp` |
| **GitLab** | Project → Settings → CI/CD → Variables → `GITLAB_STRIP_TOKEN` | Used by `.gitlab-ci.yml` job `strip-env-save` to push removal commits when `env_save` or `.env.save` are committed. Direct link: https://gitlab.com/sweeden3/canvas-lms-mcp/-/settings/ci_cd#js-cicd-variables-settings |

**Never** put the actual token value in any file, diff, or commit. Both sides use the same secret only in each provider's secret store.

## Merge strategy by source provider

When syncing the two repositories:

- **GitHub as source of truth for:** `.github/`, shared code, `.gitignore`, docs, scripts. Prefer GitHub's version for conflicts in these paths.
- **GitLab as source of truth for:** `.gitlab-ci.yml` (GitLab-specific CI). Prefer GitLab's version only for this file if you intentionally maintain GitLab-only changes.
- **Otherwise:** Prefer **GitHub** (origin) as the single source of truth; push the same branch to GitLab so both mirrors stay in sync.

## Sync workflow: add, commit, merge, sync, pull, push

1. **Add**  
   Stage the files you want to sync (e.g. CI config, docs, code):
   ```bash
   git add .github/ .gitlab-ci.yml .gitignore docs/ scripts/  # adjust paths
   ```

2. **Commit**  
   Create a commit with the changes:
   ```bash
   git commit -m "chore: sync CI/CD and docs; strip env_save/.env.save on both providers"
   ```

3. **Merge**  
   If you have a feature branch, merge into `main`:
   ```bash
   git checkout main
   git pull origin main
   git merge --no-ff <your-branch>
   ```

4. **Sync (push to both)**  
   Ensure remotes exist, then push to both:
   ```bash
   git remote add gitlab https://gitlab.com/sweeden3/canvas-lms-mcp.git   # if not already added
   git push origin main
   git push gitlab main
   ```

5. **Pull**  
   Before starting new work, pull from the source of truth:
   ```bash
   git pull origin main
   ```

6. **Push**  
   After local commits, push to both remotes to keep them in sync:
   ```bash
   git push origin main
   git push gitlab main
   ```

## Diff file (combination by provider)

The file `docs/sync-diff-ci-combined.txt` (generated below) records the combined CI-related differences between the current tree and `origin/main` for reference. It does **not** contain any secret values; it only shows configuration and code changes.

To regenerate the diff when both remotes are available:
```bash
git fetch origin
git fetch gitlab
git diff origin/main gitlab/main -- .github/ .gitlab-ci.yml > docs/sync-diff-github-vs-gitlab.txt
```
