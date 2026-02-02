# CI/CD and Repository Configuration

This project uses CI/CD pipelines on both GitHub and GitLab.

## Repositories

| Platform | URL |
|----------|-----|
| **GitHub** | https://github.com/sweeden-ttu/canvas-lms-mcp |
| **GitLab** | https://gitlab.com/sweeden3/canvas-lms-mcp |

## GitHub Actions

Workflows in `.github/workflows/`:

- **autogen-ci.yml** – Build, test, validation pipelines, GitLab sync, embeddings, agent review
- **jekyll-gh-pages.yml** – Deploy Jekyll site to GitHub Pages
- **langsmith-ci.yml** – LangSmith tracing and evaluations

On push to `main`, the autogen-ci pipeline syncs to GitLab (`gitlab.com/sweeden3/canvas-lms-mcp`).

## GitLab CI/CD

Configuration in `.gitlab-ci.yml`:

- **build** – Lint (ruff), type check (mypy)
- **test** – pytest
- **embeddings** – embed_docs, embed_mcp_server
- **agent-review** – Review-changes checklist

## Required Secrets

**GitHub** (Settings → Secrets and variables → Actions):

- `CANVAS_API_TOKEN`, `CANVAS_BASE_URL` – Canvas API
- `GITLAB_TOKEN` – GitLab OAuth/Personal Access Token (for sync)
- `LANGCHAIN_API_KEY`, `OPENAI_API_KEY` – Optional for LangSmith/AutoGen

**GitLab** (Settings → CI/CD → Variables):

- `CANVAS_API_TOKEN`, `CANVAS_BASE_URL` – Canvas API
