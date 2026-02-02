# Setup and CI/CD Documentation

This document describes local setup, GitHub Actions, and GitLab CI/CD for the Canvas LMS MCP server. It is the single reference for build, test, and deployment pipelines.

---

## Table of Contents

1. [Local Setup](#local-setup)
2. [Running the MCP Server](#running-the-mcp-server)
3. [Unit and Live Tests](#unit-and-live-tests)
4. [GitHub Actions (CI/CD)](#github-actions-cicd)
5. [GitLab CI/CD](#gitlab-cicd)
6. [Podman: Running MCP Server in a Container](#podman-running-mcp-server-in-a-container)
7. [Reproducing Failures (Podman)](#reproducing-failures-podman)
8. [Secrets and Variables](#secrets-and-variables)

---

## Local Setup

### Prerequisites

- **Python 3.10+**
- **uv** (recommended): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Canvas API token** from your Canvas instance (e.g. Texas Tech)
- **Optional:** Podman (for containerized run and CI reproduce)

### Steps

1. **Clone and enter the repo**
   ```bash
   git clone https://github.com/sweeden-ttu/canvas-lms-mcp.git
   cd canvas-lms-mcp
   ```

2. **Install dependencies**
   ```bash
   uv sync --dev
   ```
   For full extras (docker, embed): `uv sync --all-extras --dev` (embed pulls large ML deps).

3. **Configure credentials**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set:
   - `CANVAS_API_TOKEN` – your Canvas API token
   - `CANVAS_BASE_URL` – e.g. `https://texastech.instructure.com`

4. **Optional: test hints**
   Create `test_hints.json` with `valid_course_ids` and other IDs for live tests (see [CLAUDE.md](../CLAUDE.md)).

5. **Verify**
   ```bash
   uv run python -m pytest tests/ -v --tb=short
   ```

---

## Running the MCP Server

- **stdio (Claude Desktop / Claude Code):**
  ```bash
  uv run python server.py
  ```
- **Streamable HTTP (MCP Inspector, HTTP clients):**
  ```bash
  uv run python server.py --transport streamable-http --port 8000
  ```
  Then open MCP Inspector and connect to the URL (e.g. `http://localhost:8000/mcp`).

- **In Podman (HTTP):** See [Podman: Running MCP Server in a Container](#podman-running-mcp-server-in-a-container).

---

## Unit and Live Tests

- **All tests (unit + live):**
  ```bash
  uv run python -m pytest tests/ -v --tb=short
  ```
  Requires `.env` with valid `CANVAS_API_TOKEN` for live and server-unit tests.

- **Config-only unit tests (no .env required):**
  ```bash
  uv run python -m pytest tests/test_config_unit.py -v --tb=short
  ```

- **Live API tests:** `tests/test_canvas_live.py` – hit the real Canvas API. Some tests are skipped if `test_hints.json` is missing or IDs are not set.

- **Server unit tests:** `tests/test_server_unit.py` – test `_format_response`, `_handle_canvas_error`, input models, and tool registration. Skipped if `.env` is missing.

CI runs the full test suite with secrets injected (see below).

---

## GitHub Actions (CI/CD)

Workflow file: `.github/workflows/autogen-ci.yml`.

### Triggers

- **Push** to `main` or `develop`
- **Pull requests** targeting `main`
- **Schedule:** weekly (Sunday 00:00 UTC) for embeddings
- **Manual:** `workflow_dispatch` with inputs for agents, embeddings, agent review

### Jobs

| Job              | Runs on        | Description |
|------------------|----------------|-------------|
| **build-test**   | `ubuntu-latest`| Checkout, Python 3.11, uv, lint (ruff), type check (mypy), pytest. Required for downstream jobs. |
| **reproduce-failure** | `[self-hosted, podman]` | Only on build-test failure. Builds one Podman image, runs one pod, re-runs build/test steps, uploads `repro.log` and `repro-errors.txt`. See [docs/PODMAN_RUNNER.md](PODMAN_RUNNER.md). |
| **gitlab-sync**  | `ubuntu-latest`| On push to `main`: push to GitLab remote (optional). |
| **autogen-agents** | `ubuntu-latest` | When `run_agents` input is true. |
| **embeddings**   | `ubuntu-latest`| On schedule or when `run_embeddings` is true. Runs `embed_docs.py` and `embed_mcp_server.py` for each `mcp/*/` submodule, uploads artifacts. |
| **agent-review** | `ubuntu-latest`| On PR or when `run_agent_review` is true. Re-runs tests and prints review-changes checklist. |
| **generate-badges** | `ubuntu-latest` | After build-test and gitlab-sync; updates badge JSON under `.github/badges/`. |

### Build and test steps (build-test)

1. Checkout (fetch-depth 0)
2. Setup Python 3.11
3. Install uv (with cache)
4. `uv sync --all-extras --dev`
5. `uv run ruff check .`
6. `uv run mypy server.py --ignore-missing-imports`
7. `uv run pytest tests/ -v --tb=short` with `CANVAS_API_TOKEN` and `CANVAS_BASE_URL` from secrets

### Required secrets (GitHub)

- **CANVAS_API_TOKEN** – Canvas API token (for tests and live API)
- **CANVAS_BASE_URL** – Canvas base URL (e.g. `https://texastech.instructure.com`)
- **GITLAB_TOKEN** (optional) – for gitlab-sync
- **GITLAB_PROJECT_PATH** (optional) – e.g. `username/canvas-lms-mcp`
- **OPENAI_API_KEY** (optional) – for autogen-agents

---

## GitLab CI/CD

Config file: `.gitlab-ci.yml`.

### Stages

1. **build** – Lint and type check
2. **test** – Pytest (uses build artifacts)
3. **embeddings** – Optional; embed docs and MCP servers
4. **agent-review** – Optional; review-changes checklist

### Jobs

| Job           | Stage        | Description |
|---------------|--------------|-------------|
| **build**     | build        | `uv sync --all-extras --dev`, ruff, mypy. Artifacts: `.venv/`, `.uv-cache/`. |
| **test**      | test         | Depends on build; runs `uv run pytest tests/ -v --tb=short`. Uses `CANVAS_API_TOKEN`, `CANVAS_BASE_URL`. |
| **embeddings** | embeddings | Scheduled or on changes to docs/skills/agents/rules/worktrees/embed scripts/mcp. Runs embed_docs and embed_mcp_server; can be manual. |
| **agent-review** | agent-review | On merge request or manual. Re-runs tests and echoes review checklist; `allow_failure: true`. |

### Variables (GitLab)

- **CANVAS_API_TOKEN** – Project/group CI variable (masked)
- **CANVAS_BASE_URL** – Canvas base URL
- **PYTHON_VERSION** – `3.11`
- **UV_CACHE_DIR** – `.uv-cache`

---

## Podman: Running MCP Server in a Container

You can run the Canvas MCP server in Podman in **streamable-http** mode for local testing (e.g. MCP Inspector).

### Script

From the repo root:

```bash
./scripts/run_canvas_mcp_podman.sh
```

This script:

1. Builds the image from the project `Dockerfile` (tag: `canvas-lms-mcp:latest` by default).
2. Runs a container with the entrypoint command **http** (streamable-http on port 8000).
3. Passes `CANVAS_API_TOKEN` and `CANVAS_BASE_URL` from the environment (or from `.env` if present).

Override with env vars:

```bash
IMAGE_NAME=my-canvas-mcp CONTAINER_NAME=my-mcp PORT=9000 ./scripts/run_canvas_mcp_podman.sh
```

After starting, the MCP server is available at `http://localhost:8000` (or the chosen port). Use MCP Inspector or another HTTP MCP client to connect.

To run the server in **stdio** mode (e.g. for Claude Desktop), run it on the host with `uv run python server.py`; stdio is not suitable for a long-running container in the same way.

---

## Reproducing Failures (Podman)

When the GitHub **build-test** job fails, the **reproduce-failure** job (on a self-hosted runner with label `podman`) can reproduce the failure inside a Podman container.

- **Script:** `.github/reproduce/run-repro.sh`
- **Image:** `.github/reproduce/Dockerfile.repro` (Debian Bookworm, uv, project copy, same ruff/mypy/pytest steps as build-test).

Run locally (from repo root, with Podman):

```bash
chmod +x .github/reproduce/run-repro.sh
.github/reproduce/run-repro.sh .
```

Optional env: `CANVAS_API_TOKEN`, `CANVAS_BASE_URL`, `IMAGE_NAME`, `POD_NAME`, `LOG_FILE`, `ERRORS_FILE`. Outputs: `repro.log`, `repro-errors.txt`.

See [PODMAN_RUNNER.md](PODMAN_RUNNER.md) for setting up the self-hosted runner with Podman.

---

## Secrets and Variables

| Name               | Where       | Purpose |
|--------------------|------------|---------|
| CANVAS_API_TOKEN   | GitHub secrets, GitLab CI variables, local `.env` | Canvas API auth for tests and MCP server |
| CANVAS_BASE_URL    | GitHub secrets, GitLab CI variables, local `.env` | Canvas instance URL |
| GITLAB_TOKEN       | GitHub secrets | GitLab push (gitlab-sync) |
| GITLAB_PROJECT_PATH| GitHub secrets | GitLab repo path for sync |
| OPENAI_API_KEY     | GitHub secrets | AutoGen agents (optional) |

Never commit `.env` or real tokens. CI should use secrets/variables only.

---

## Quick Reference

| Task                    | Command or location |
|-------------------------|----------------------|
| Local tests             | `uv run python -m pytest tests/ -v --tb=short` |
| Run MCP (stdio)         | `uv run python server.py` |
| Run MCP (HTTP)          | `uv run python server.py --transport streamable-http --port 8000` |
| Run MCP in Podman       | `./scripts/run_canvas_mcp_podman.sh` |
| Reproduce CI failure    | `.github/reproduce/run-repro.sh .` |
| GitHub workflow         | `.github/workflows/autogen-ci.yml` |
| GitLab pipeline         | `.gitlab-ci.yml` |
| Podman runner setup     | [docs/PODMAN_RUNNER.md](PODMAN_RUNNER.md) |
