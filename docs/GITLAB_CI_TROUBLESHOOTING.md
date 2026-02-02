# GitLab CI troubleshooting

## Viewing pipeline and job logs

Without API access you can:

1. **Web:** Project → **CI/CD → Pipelines** → click pipeline ID → click failed job to see logs.
2. **glab (with token):**  
   ```bash
   echo "YOUR_GITLAB_TOKEN" | glab auth login --hostname gitlab.com --stdin
   glab ci view PIPELINE_ID -R sweeden3/canvas-lms-mcp
   glab ci trace JOB_ID -R sweeden3/canvas-lms-mcp
   ```
3. **API:**  
   `GET /projects/:id/pipelines/:pipeline_id` and  
   `GET /projects/:id/jobs?pipeline_id=:pipeline_id`  
   (requires `PRIVATE-TOKEN` or `Job-Token`).

## Common fixes applied

- **Build job – git fetch:** Use `ref="${CI_COMMIT_REF_NAME:-main}"` and `|| true` so a failed fetch (e.g. wrong ref or network) does not fail the whole job; build continues with the current checkout.
- **Strip-env-save:** Push requires `GITLAB_STRIP_TOKEN` in CI/CD variables; job has `allow_failure: true` so the pipeline continues if push fails.

## Pipeline 2301432468

If this pipeline failed, check the failed job’s logs in the GitLab UI (CI/CD → Pipelines → 2301432468 → failed job). Typical causes: git fetch ref, `uv sync`, ruff/mypy, or missing CI/CD variables (`CANVAS_API_TOKEN`, `CANVAS_BASE_URL`, `GITLAB_STRIP_TOKEN`).
