# Microsoft AutoGen Integration

[![AutoGen CI/CD](https://img.shields.io/github/actions/workflow/status/sweeden-ttu/canvas-lms-mcp/autogen-ci.yml?label=AutoGen%20CI&logo=github)](https://github.com/sweeden-ttu/canvas-lms-mcp/actions/workflows/autogen-ci.yml)
[![GitLab Sync](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab)](https://gitlab.com/sweeden-ttu/canvas-lms-mcp)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![AutoGen](https://img.shields.io/badge/AutoGen-0.3+-purple?logo=microsoft)](https://microsoft.github.io/autogen/)

This guide covers integrating the Canvas LMS MCP Server with Microsoft AutoGen for multi-agent AI workflows, including CI/CD pipelines and GitHub/GitLab synchronization.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [AutoGen Agent Configuration](#autogen-agent-configuration)
- [CI/CD Integration](#cicd-integration)
- [GitHub/GitLab Synchronization](#githubgitlab-synchronization)
- [Badge Generation](#badge-generation)
- [Troubleshooting](#troubleshooting)

---

## Overview

Microsoft AutoGen enables building multi-agent systems where AI agents collaborate to solve complex tasks. This integration allows:

- **Canvas MCP Agent**: Interfaces with Canvas LMS via the MCP server
- **CI/CD Agent**: Manages build, test, and deployment pipelines
- **Sync Agent**: Keeps GitHub and GitLab repositories synchronized
- **Badge Agent**: Generates status badges and thumbnails

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoGen Orchestrator                      │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│ Canvas MCP  │   CI/CD     │    Sync     │      Badge        │
│   Agent     │   Agent     │   Agent     │      Agent        │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ Canvas LMS  │ GitHub      │ GitHub ↔    │ shields.io        │
│ API         │ Actions     │ GitLab      │ badgen.net        │
└─────────────┴─────────────┴─────────────┴───────────────────┘
```

---

## Prerequisites

- Python 3.10+
- uv package manager
- GitHub account with Actions enabled
- GitLab account (for sync)
- Canvas API token
- OpenAI or Azure OpenAI API key (for AutoGen LLM)

---

## Installation

### 1. Install AutoGen Dependencies

```bash
cd canvas-lms-mcp

# Add AutoGen dependencies
uv add "pyautogen>=0.3.0" "openai>=1.0.0"

# Optional: Add Azure OpenAI support
uv add "azure-identity>=1.15.0"
```

### 2. Configure Environment

Add to your `.env` file:

```env
# Canvas LMS Configuration
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_BASE_URL=https://texastech.instructure.com

# AutoGen LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
# OR for Azure OpenAI:
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4

# GitLab Sync Configuration
GITLAB_TOKEN=your_gitlab_token_here
GITLAB_PROJECT_ID=your_project_id
```

---

## AutoGen Agent Configuration

### Create Agent Configuration File

**`autogen_config.py`:**

```python
"""AutoGen agent configuration for Canvas LMS MCP integration."""

import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

# LLM Configuration
LLM_CONFIG = {
    "config_list": [
        {
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ],
    "temperature": 0.1,
    "timeout": 120,
}

# Canvas MCP Agent - Interfaces with Canvas LMS
canvas_agent = AssistantAgent(
    name="CanvasMCPAgent",
    system_message="""You are an expert at interfacing with Canvas LMS via the MCP server.
    You can:
    - List courses and enrollments
    - Retrieve assignments, modules, and grades
    - Fetch announcements and discussion topics
    - Access calendar events and planner items
    
    Use the MCP tools available to query Canvas data. Always format responses
    clearly and handle errors gracefully.""",
    llm_config=LLM_CONFIG,
)

# CI/CD Agent - Manages build and deployment pipelines
cicd_agent = AssistantAgent(
    name="CICDAgent",
    system_message="""You are an expert CI/CD engineer specializing in GitHub Actions and GitLab CI.
    You can:
    - Create and modify workflow YAML files
    - Configure build, test, and deployment stages
    - Set up environment secrets and variables
    - Debug pipeline failures
    - Generate status badges
    
    Follow best practices for CI/CD security and efficiency.""",
    llm_config=LLM_CONFIG,
)

# Sync Agent - Synchronizes GitHub and GitLab repositories
sync_agent = AssistantAgent(
    name="SyncAgent",
    system_message="""You are an expert at repository synchronization between GitHub and GitLab.
    You can:
    - Configure bidirectional mirroring
    - Handle merge conflicts during sync
    - Set up webhooks for real-time synchronization
    - Manage branch protection rules on both platforms
    - Handle large file storage (LFS) synchronization
    
    Ensure data integrity and maintain commit history during sync operations.""",
    llm_config=LLM_CONFIG,
)

# Badge Agent - Generates status badges and thumbnails
badge_agent = AssistantAgent(
    name="BadgeAgent",
    system_message="""You are an expert at generating status badges and thumbnails for repositories.
    You can:
    - Create shields.io badge URLs
    - Generate custom badge images
    - Configure dynamic badges from CI/CD status
    - Create workflow status badges
    - Design repository thumbnail images
    
    Always provide markdown-ready badge code.""",
    llm_config=LLM_CONFIG,
)

# User Proxy Agent - Executes code and interacts with user
user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "autogen_workspace",
        "use_docker": False,
    },
)


def create_group_chat():
    """Create a group chat with all agents."""
    group_chat = GroupChat(
        agents=[user_proxy, canvas_agent, cicd_agent, sync_agent, badge_agent],
        messages=[],
        max_round=20,
    )
    
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=LLM_CONFIG,
    )
    
    return group_chat, manager


def run_task(task: str):
    """Run a task using the agent group."""
    group_chat, manager = create_group_chat()
    user_proxy.initiate_chat(manager, message=task)
    return group_chat.messages
```

### Usage Example

```python
from autogen_config import run_task

# Example: Sync repos and generate badges
result = run_task("""
    1. Check the current GitHub Actions workflow status
    2. Sync the repository to GitLab
    3. Generate updated status badges for:
       - Build status
       - Test coverage
       - GitLab sync status
    4. Update the README with the new badges
""")
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create **`.github/workflows/autogen-ci.yml`**:

```yaml
name: AutoGen CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  PYTHON_VERSION: "3.11"
  UV_CACHE_DIR: /tmp/.uv-cache

jobs:
  # ============================================
  # Build and Test Stage
  # ============================================
  build-test:
    name: Build & Test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for sync

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run linting
        run: uv run ruff check .

      - name: Run type checking
        run: uv run mypy server.py

      - name: Run tests
        run: uv run pytest tests/ -v --tb=short
        env:
          CANVAS_API_TOKEN: ${{ secrets.CANVAS_API_TOKEN }}
          CANVAS_BASE_URL: ${{ secrets.CANVAS_BASE_URL }}

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: false

  # ============================================
  # GitLab Sync Stage
  # ============================================
  gitlab-sync:
    name: Sync to GitLab
    runs-on: ubuntu-latest
    needs: build-test
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Push to GitLab
        run: |
          git remote add gitlab https://oauth2:${{ secrets.GITLAB_TOKEN }}@gitlab.com/${{ secrets.GITLAB_PROJECT_PATH }}.git || true
          git push gitlab main --force
          git push gitlab --tags --force
        env:
          GITLAB_TOKEN: ${{ secrets.GITLAB_TOKEN }}

      - name: Notify sync complete
        run: |
          echo "::notice::Successfully synced to GitLab"

  # ============================================
  # AutoGen Agent Stage
  # ============================================
  autogen-agents:
    name: Run AutoGen Agents
    runs-on: ubuntu-latest
    needs: build-test
    if: github.event_name == 'workflow_dispatch'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install AutoGen dependencies
        run: |
          uv sync
          uv add pyautogen openai

      - name: Run AutoGen pipeline
        run: |
          uv run python -c "
          from autogen_config import run_task
          run_task('Generate status report for CI/CD pipeline')
          "
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CANVAS_API_TOKEN: ${{ secrets.CANVAS_API_TOKEN }}

  # ============================================
  # Badge Generation Stage
  # ============================================
  generate-badges:
    name: Generate Status Badges
    runs-on: ubuntu-latest
    needs: [build-test, gitlab-sync]
    if: always()
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate badge JSON
        run: |
          mkdir -p .github/badges
          
          # Build status badge
          if [ "${{ needs.build-test.result }}" == "success" ]; then
            echo '{"schemaVersion":1,"label":"build","message":"passing","color":"brightgreen"}' > .github/badges/build.json
          else
            echo '{"schemaVersion":1,"label":"build","message":"failing","color":"red"}' > .github/badges/build.json
          fi
          
          # Sync status badge
          if [ "${{ needs.gitlab-sync.result }}" == "success" ]; then
            echo '{"schemaVersion":1,"label":"GitLab Sync","message":"synced","color":"orange"}' > .github/badges/sync.json
          else
            echo '{"schemaVersion":1,"label":"GitLab Sync","message":"pending","color":"yellow"}' > .github/badges/sync.json
          fi

      - name: Commit badge updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .github/badges/
          git diff --staged --quiet || git commit -m "chore: update status badges [skip ci]"
          git push
```

### GitLab CI Configuration

Create **`.gitlab-ci.yml`** for GitLab-side pipeline:

```yaml
stages:
  - build
  - test
  - sync
  - badges

variables:
  PYTHON_VERSION: "3.11"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - .venv/

# ============================================
# Build Stage
# ============================================
build:
  stage: build
  image: python:${PYTHON_VERSION}
  script:
    - pip install uv
    - uv sync --all-extras --dev
  artifacts:
    paths:
      - .venv/
    expire_in: 1 hour

# ============================================
# Test Stage
# ============================================
test:
  stage: test
  image: python:${PYTHON_VERSION}
  dependencies:
    - build
  script:
    - pip install uv
    - uv run pytest tests/ -v
  coverage: '/TOTAL.*\s+(\d+%)$/'

lint:
  stage: test
  image: python:${PYTHON_VERSION}
  dependencies:
    - build
  script:
    - pip install uv
    - uv run ruff check .
    - uv run mypy server.py
  allow_failure: true

# ============================================
# GitHub Sync Stage
# ============================================
sync-to-github:
  stage: sync
  image: alpine/git
  only:
    - main
  script:
    - git remote add github https://oauth2:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git || true
    - git push github HEAD:main --force
    - git push github --tags --force
  when: manual

# ============================================
# Badge Generation
# ============================================
generate-badges:
  stage: badges
  image: alpine
  script:
    - mkdir -p public/badges
    - |
      cat > public/badges/gitlab-build.json << EOF
      {"schemaVersion":1,"label":"GitLab Build","message":"passing","color":"fc6d26"}
      EOF
  artifacts:
    paths:
      - public/badges/
```

---

## GitHub/GitLab Synchronization

### Sync Agent Implementation

**`sync_agent.py`:**

```python
"""Repository synchronization agent for GitHub and GitLab."""

import os
import subprocess
from dataclasses import dataclass
from typing import Optional
import httpx


@dataclass
class SyncConfig:
    """Configuration for repository synchronization."""
    github_repo: str
    github_token: str
    gitlab_project_id: str
    gitlab_token: str
    gitlab_url: str = "https://gitlab.com"


class RepositorySyncAgent:
    """Agent for synchronizing repositories between GitHub and GitLab."""
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self.github_api = "https://api.github.com"
    
    async def sync_github_to_gitlab(self, branch: str = "main") -> dict:
        """Sync GitHub repository to GitLab."""
        result = {"status": "pending", "details": []}
        
        try:
            # Clone from GitHub
            clone_url = f"https://oauth2:{self.config.github_token}@github.com/{self.config.github_repo}.git"
            subprocess.run(
                ["git", "clone", "--mirror", clone_url, "repo_mirror"],
                check=True,
                capture_output=True
            )
            result["details"].append("Cloned from GitHub")
            
            # Push to GitLab
            gitlab_url = f"https://oauth2:{self.config.gitlab_token}@gitlab.com/{self.config.gitlab_project_id}.git"
            subprocess.run(
                ["git", "-C", "repo_mirror", "push", "--mirror", gitlab_url],
                check=True,
                capture_output=True
            )
            result["details"].append("Pushed to GitLab")
            
            result["status"] = "success"
            
        except subprocess.CalledProcessError as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        finally:
            # Cleanup
            subprocess.run(["rm", "-rf", "repo_mirror"], capture_output=True)
        
        return result
    
    async def get_sync_status(self) -> dict:
        """Get current synchronization status."""
        async with httpx.AsyncClient() as client:
            # Check GitHub
            github_resp = await client.get(
                f"{self.github_api}/repos/{self.config.github_repo}/commits/main",
                headers={"Authorization": f"Bearer {self.config.github_token}"}
            )
            github_sha = github_resp.json().get("sha", "unknown")[:7]
            
            # Check GitLab
            gitlab_resp = await client.get(
                f"{self.config.gitlab_url}/api/v4/projects/{self.config.gitlab_project_id}/repository/commits/main",
                headers={"PRIVATE-TOKEN": self.config.gitlab_token}
            )
            gitlab_sha = gitlab_resp.json().get("id", "unknown")[:7]
            
            return {
                "github_sha": github_sha,
                "gitlab_sha": gitlab_sha,
                "in_sync": github_sha == gitlab_sha,
            }
    
    def generate_sync_badge(self, in_sync: bool) -> str:
        """Generate markdown badge for sync status."""
        if in_sync:
            return "![GitLab Sync](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab)"
        else:
            return "![GitLab Sync](https://img.shields.io/badge/GitLab-Out%20of%20Sync-red?logo=gitlab)"
```

### Webhook Configuration

**GitHub Webhook Setup:**

1. Go to Repository Settings > Webhooks > Add webhook
2. Payload URL: `https://gitlab.com/api/v4/projects/{PROJECT_ID}/mirror/pull`
3. Content type: `application/json`
4. Events: Push, Release

**GitLab Mirroring Setup:**

1. Go to Project Settings > Repository > Mirroring repositories
2. Git repository URL: `https://github.com/{OWNER}/{REPO}.git`
3. Mirror direction: Pull
4. Authentication method: Password (use GitHub PAT)

---

## Badge Generation

### Available Badge Types

| Badge Type | Markdown | Preview |
|------------|----------|---------|
| Build Status | `![Build](https://img.shields.io/github/actions/workflow/status/user/repo/ci.yml)` | ![Build](https://img.shields.io/badge/build-passing-brightgreen) |
| GitLab Sync | `![Sync](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab)` | ![Sync](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab) |
| AutoGen | `![AutoGen](https://img.shields.io/badge/AutoGen-Enabled-purple?logo=microsoft)` | ![AutoGen](https://img.shields.io/badge/AutoGen-Enabled-purple?logo=microsoft) |
| Python | `![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)` | ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python) |
| Coverage | `![Coverage](https://img.shields.io/codecov/c/github/user/repo)` | ![Coverage](https://img.shields.io/badge/coverage-85%25-green) |

### Badge Generator Script

**`scripts/generate_badges.py`:**

```python
"""Generate status badges for the repository."""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Literal


@dataclass
class Badge:
    """Represents a status badge."""
    label: str
    message: str
    color: str
    logo: str = ""
    
    def to_shields_url(self) -> str:
        """Generate shields.io URL."""
        base = f"https://img.shields.io/badge/{self.label}-{self.message}-{self.color}"
        if self.logo:
            base += f"?logo={self.logo}"
        return base.replace(" ", "%20")
    
    def to_markdown(self, alt_text: str = "") -> str:
        """Generate markdown image."""
        alt = alt_text or self.label
        return f"![{alt}]({self.to_shields_url()})"
    
    def to_json(self) -> dict:
        """Generate endpoint JSON for dynamic badges."""
        return {
            "schemaVersion": 1,
            "label": self.label,
            "message": self.message,
            "color": self.color,
        }


def generate_all_badges(output_dir: Path) -> list[str]:
    """Generate all project badges."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    badges = [
        Badge("build", "passing", "brightgreen", "github"),
        Badge("AutoGen", "enabled", "purple", "microsoft"),
        Badge("GitLab", "synced", "orange", "gitlab"),
        Badge("Python", "3.10+", "blue", "python"),
        Badge("MCP", "active", "green"),
    ]
    
    markdown_lines = []
    
    for badge in badges:
        # Save JSON endpoint
        json_path = output_dir / f"{badge.label.lower()}.json"
        json_path.write_text(json.dumps(badge.to_json(), indent=2))
        
        # Collect markdown
        markdown_lines.append(badge.to_markdown())
    
    return markdown_lines


if __name__ == "__main__":
    badges_dir = Path(".github/badges")
    markdown = generate_all_badges(badges_dir)
    print("Badge Markdown:")
    print(" ".join(markdown))
```

---

## Troubleshooting

### Common Issues

**AutoGen connection timeout:**
```python
# Increase timeout in LLM config
LLM_CONFIG = {
    "timeout": 300,  # 5 minutes
    "max_retries": 3,
}
```

**GitLab sync authentication failure:**
```bash
# Verify GitLab token has write_repository scope
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/$PROJECT_ID"
```

**GitHub Actions secrets not available:**
- Ensure secrets are set in repository Settings > Secrets and variables > Actions
- Check workflow has correct permissions in `GITHUB_TOKEN` scope

### Logs and Debugging

```bash
# View AutoGen agent logs
export AUTOGEN_LOG_LEVEL=DEBUG
uv run python autogen_config.py

# Test GitLab sync manually
git remote add gitlab https://oauth2:$GITLAB_TOKEN@gitlab.com/user/repo.git
git push gitlab main --dry-run
```

---

## Related Documentation

- [Microsoft AutoGen Documentation](https://microsoft.github.io/autogen/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Shields.io Badge Service](https://shields.io/)
- [Canvas LMS MCP Server](../README.md)
