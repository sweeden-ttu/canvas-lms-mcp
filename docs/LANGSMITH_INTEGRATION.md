# LangSmith Integration

[![LangSmith Tracing](https://img.shields.io/badge/LangSmith-Enabled-00A67E?logo=langchain)](https://smith.langchain.com/)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/sweeden-ttu/canvas-lms-mcp/langsmith-ci.yml?label=LangSmith%20CI&logo=github)](https://github.com/sweeden-ttu/canvas-lms-mcp/actions/workflows/langsmith-ci.yml)
[![GitLab Sync](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab)](https://gitlab.com/sweeden-ttu/canvas-lms-mcp)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)

This guide covers integrating the Canvas LMS MCP Server with LangSmith for LLM observability, tracing, evaluation, and CI/CD workflows with GitHub/GitLab synchronization.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [LangSmith Configuration](#langsmith-configuration)
- [Tracing Integration](#tracing-integration)
- [CI/CD Integration](#cicd-integration)
- [GitHub/GitLab Synchronization](#githubgitlab-synchronization)
- [Evaluation Workflows](#evaluation-workflows)
- [Badge Generation](#badge-generation)
- [Troubleshooting](#troubleshooting)

---

## Overview

LangSmith provides observability and evaluation for LLM applications. This integration enables:

- **Tracing**: Full visibility into MCP tool calls and LLM interactions
- **Evaluation**: Automated testing of LLM responses
- **CI/CD**: Integration with GitHub Actions and GitLab CI
- **Sync Agent**: Repository synchronization between platforms
- **Monitoring**: Real-time dashboards and alerts

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangSmith Platform                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│    Tracing      │   Evaluation    │        Monitoring           │
│    Service      │    Datasets     │        Dashboard            │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                         ↑ API                                    │
├─────────────────────────────────────────────────────────────────┤
│                    Canvas LMS MCP Server                         │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│ MCP Tools   │ LangChain   │   CI/CD     │    Sync Agent         │
│ (traced)    │ Integration │   Pipeline  │ (GitHub ↔ GitLab)     │
└─────────────┴─────────────┴─────────────┴───────────────────────┘
```

---

## Prerequisites

- Python 3.10+
- uv package manager
- [LangSmith account](https://smith.langchain.com/) (free tier available)
- GitHub account with Actions enabled
- GitLab account (for sync)
- Canvas API token

---

## Installation

### 1. Install LangSmith Dependencies

```bash
cd canvas-lms-mcp

# Add LangSmith and LangChain dependencies
uv add langsmith langchain langchain-openai

# Optional: Add evaluation dependencies
uv add --dev pytest-langsmith
```

### 2. Configure Environment

Add to your `.env` file:

```env
# Canvas LMS Configuration
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_BASE_URL=https://texastech.instructure.com

# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=canvas-lms-mcp

# OpenAI Configuration (for LangChain)
OPENAI_API_KEY=your_openai_api_key_here

# GitLab Sync Configuration
GITLAB_TOKEN=your_gitlab_token_here
GITLAB_PROJECT_ID=your_project_id
GITHUB_TOKEN=your_github_pat_here
```

---

## LangSmith Configuration

### Project Setup

1. Go to [LangSmith](https://smith.langchain.com/)
2. Create a new project: `canvas-lms-mcp`
3. Copy your API key from Settings > API Keys
4. Add the key to your `.env` file

### Configuration File

**`langsmith_config.py`:**

```python
"""LangSmith configuration for Canvas LMS MCP integration."""

import os
from langsmith import Client
from langsmith.run_trees import RunTree

# Initialize LangSmith client
client = Client(
    api_url=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
    api_key=os.getenv("LANGCHAIN_API_KEY"),
)

# Project configuration
PROJECT_NAME = os.getenv("LANGCHAIN_PROJECT", "canvas-lms-mcp")


def get_run_tree(name: str, run_type: str = "chain") -> RunTree:
    """Create a new run tree for tracing."""
    return RunTree(
        name=name,
        run_type=run_type,
        project_name=PROJECT_NAME,
    )


def trace_mcp_tool(tool_name: str):
    """Decorator to trace MCP tool calls."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            run_tree = get_run_tree(f"mcp_tool:{tool_name}", run_type="tool")
            run_tree.add_metadata({
                "tool_name": tool_name,
                "args": str(args),
                "kwargs": str(kwargs),
            })
            
            try:
                result = await func(*args, **kwargs)
                run_tree.end(outputs={"result": str(result)[:1000]})
                run_tree.post()
                return result
            except Exception as e:
                run_tree.end(error=str(e))
                run_tree.post()
                raise
        
        return wrapper
    return decorator


def check_connection() -> bool:
    """Verify LangSmith connection."""
    try:
        # List projects to verify connection
        projects = list(client.list_projects(limit=1))
        return True
    except Exception as e:
        print(f"LangSmith connection failed: {e}")
        return False
```

---

## Tracing Integration

### Trace MCP Tool Calls

**`traced_server.py`:**

```python
"""Canvas LMS MCP Server with LangSmith tracing."""

import os
from functools import wraps
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

from mcp.server.fastmcp import FastMCP
from config import load_env_config, get_api_headers

# Enable tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"

mcp = FastMCP(name="canvas_mcp_traced")
_config = load_env_config()


def trace_tool(name: str):
    """Decorator to trace tool execution in LangSmith."""
    def decorator(func):
        @wraps(func)
        @traceable(name=name, run_type="tool")
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


@mcp.tool(name="canvas_list_courses")
@trace_tool("canvas_list_courses")
async def canvas_list_courses(params: dict) -> str:
    """List courses with LangSmith tracing."""
    import httpx
    
    async with httpx.AsyncClient(
        base_url=_config.base_url,
        headers=get_api_headers(_config.api_token),
        timeout=30.0
    ) as client:
        response = await client.get(
            "/api/v1/courses",
            params={"enrollment_state": "active", "per_page": 50}
        )
        response.raise_for_status()
        return str(response.json())


@mcp.tool(name="canvas_get_assignments")
@trace_tool("canvas_get_assignments")
async def canvas_get_assignments(params: dict) -> str:
    """Get assignments with LangSmith tracing."""
    import httpx
    
    course_id = params.get("course_id")
    
    async with httpx.AsyncClient(
        base_url=_config.base_url,
        headers=get_api_headers(_config.api_token),
        timeout=30.0
    ) as client:
        response = await client.get(
            f"/api/v1/courses/{course_id}/assignments",
            params={"per_page": 50}
        )
        response.raise_for_status()
        return str(response.json())
```

### LangChain Integration

**`langchain_canvas.py`:**

```python
"""LangChain integration for Canvas LMS queries."""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable

import httpx
from config import load_env_config, get_api_headers

_config = load_env_config()


async def fetch_courses() -> str:
    """Fetch Canvas courses."""
    async with httpx.AsyncClient(
        base_url=_config.base_url,
        headers=get_api_headers(_config.api_token),
        timeout=30.0
    ) as client:
        response = await client.get("/api/v1/courses", params={"per_page": 50})
        return str(response.json())


async def fetch_assignments(course_id: str) -> str:
    """Fetch assignments for a course."""
    async with httpx.AsyncClient(
        base_url=_config.base_url,
        headers=get_api_headers(_config.api_token),
        timeout=30.0
    ) as client:
        response = await client.get(f"/api/v1/courses/{course_id}/assignments")
        return str(response.json())


# Define LangChain tools
canvas_tools = [
    Tool(
        name="list_courses",
        description="List all Canvas courses the user is enrolled in",
        func=lambda x: fetch_courses(),
        coroutine=fetch_courses,
    ),
    Tool(
        name="get_assignments",
        description="Get assignments for a specific course. Input: course_id",
        func=lambda course_id: fetch_assignments(course_id),
        coroutine=fetch_assignments,
    ),
]


@traceable(name="canvas_query_agent")
def create_canvas_agent():
    """Create a LangChain agent for Canvas queries."""
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that can query Canvas LMS.
        Use the available tools to fetch course information, assignments, and other data.
        Always provide clear, formatted responses."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_openai_tools_agent(llm, canvas_tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=canvas_tools,
        verbose=True,
        handle_parsing_errors=True,
    )


@traceable(name="query_canvas")
async def query_canvas(question: str) -> str:
    """Query Canvas using the LangChain agent."""
    agent = create_canvas_agent()
    result = await agent.ainvoke({"input": question})
    return result["output"]
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create **`.github/workflows/langsmith-ci.yml`**:

```yaml
name: LangSmith CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # Run evaluations daily at 6 AM UTC
    - cron: '0 6 * * *'
  workflow_dispatch:
    inputs:
      run_evaluations:
        description: 'Run LangSmith evaluations'
        required: false
        default: 'false'
        type: boolean

env:
  PYTHON_VERSION: "3.11"
  LANGCHAIN_TRACING_V2: "true"
  LANGCHAIN_PROJECT: "canvas-lms-mcp-ci"

jobs:
  # ============================================
  # Build and Lint Stage
  # ============================================
  build:
    name: Build & Lint
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Install dependencies
        run: |
          uv sync --all-extras --dev
          uv add langsmith langchain langchain-openai

      - name: Run linting
        run: uv run ruff check .

      - name: Run type checking
        run: uv run mypy server.py --ignore-missing-imports

  # ============================================
  # Unit Tests with Tracing
  # ============================================
  test:
    name: Test with LangSmith Tracing
    runs-on: ubuntu-latest
    needs: build
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Install dependencies
        run: |
          uv sync --all-extras --dev
          uv add langsmith langchain

      - name: Run tests with tracing
        run: uv run pytest tests/ -v --tb=short
        env:
          LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
          LANGCHAIN_ENDPOINT: https://api.smith.langchain.com
          LANGCHAIN_PROJECT: ${{ env.LANGCHAIN_PROJECT }}
          CANVAS_API_TOKEN: ${{ secrets.CANVAS_API_TOKEN }}
          CANVAS_BASE_URL: ${{ secrets.CANVAS_BASE_URL }}

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: pytest-results.xml

  # ============================================
  # LangSmith Evaluations
  # ============================================
  evaluate:
    name: Run LangSmith Evaluations
    runs-on: ubuntu-latest
    needs: test
    if: github.event.inputs.run_evaluations == 'true' || github.event_name == 'schedule'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: |
          uv sync --all-extras --dev
          uv add langsmith langchain langchain-openai

      - name: Run LangSmith evaluations
        run: |
          uv run python scripts/run_evaluations.py
        env:
          LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
          LANGCHAIN_PROJECT: ${{ env.LANGCHAIN_PROJECT }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CANVAS_API_TOKEN: ${{ secrets.CANVAS_API_TOKEN }}

      - name: Generate evaluation report
        run: |
          uv run python scripts/generate_eval_report.py > evaluation_report.md

      - name: Upload evaluation report
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-report
          path: evaluation_report.md

      - name: Comment on PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('evaluation_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## LangSmith Evaluation Results\n\n${report}`
            });

  # ============================================
  # GitLab Sync Stage
  # ============================================
  gitlab-sync:
    name: Sync to GitLab
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Push to GitLab
        run: |
          git remote add gitlab https://oauth2:${{ secrets.GITLAB_TOKEN }}@gitlab.com/${{ secrets.GITLAB_PROJECT_PATH }}.git || true
          git push gitlab main --force
          git push gitlab --tags --force

      - name: Update sync status
        run: |
          echo "SYNC_STATUS=success" >> $GITHUB_ENV
          echo "SYNC_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $GITHUB_ENV

      - name: Notify sync complete
        run: |
          echo "::notice title=GitLab Sync::Successfully synced to GitLab at ${{ env.SYNC_TIME }}"

  # ============================================
  # Badge Generation
  # ============================================
  generate-badges:
    name: Generate Status Badges
    runs-on: ubuntu-latest
    needs: [test, evaluate, gitlab-sync]
    if: always() && github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate badge JSON files
        run: |
          mkdir -p .github/badges
          
          # Test status
          if [ "${{ needs.test.result }}" == "success" ]; then
            echo '{"schemaVersion":1,"label":"tests","message":"passing","color":"brightgreen"}' > .github/badges/tests.json
          else
            echo '{"schemaVersion":1,"label":"tests","message":"failing","color":"red"}' > .github/badges/tests.json
          fi
          
          # LangSmith status
          if [ "${{ needs.evaluate.result }}" == "success" ]; then
            echo '{"schemaVersion":1,"label":"LangSmith","message":"passing","color":"00A67E"}' > .github/badges/langsmith.json
          elif [ "${{ needs.evaluate.result }}" == "skipped" ]; then
            echo '{"schemaVersion":1,"label":"LangSmith","message":"skipped","color":"yellow"}' > .github/badges/langsmith.json
          else
            echo '{"schemaVersion":1,"label":"LangSmith","message":"failing","color":"red"}' > .github/badges/langsmith.json
          fi
          
          # GitLab sync status
          if [ "${{ needs.gitlab-sync.result }}" == "success" ]; then
            echo '{"schemaVersion":1,"label":"GitLab","message":"synced","color":"fc6d26"}' > .github/badges/gitlab.json
          else
            echo '{"schemaVersion":1,"label":"GitLab","message":"pending","color":"yellow"}' > .github/badges/gitlab.json
          fi

      - name: Commit badge updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .github/badges/
          git diff --staged --quiet || git commit -m "chore: update status badges [skip ci]"
          git push
```

### Evaluation Script

Create **`scripts/run_evaluations.py`**:

```python
"""Run LangSmith evaluations for Canvas LMS MCP."""

import os
from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

# Initialize client
client = Client()

# Define evaluation dataset
DATASET_NAME = "canvas-mcp-eval"


def create_evaluation_dataset():
    """Create or update the evaluation dataset."""
    # Check if dataset exists
    datasets = list(client.list_datasets(dataset_name=DATASET_NAME))
    
    if not datasets:
        dataset = client.create_dataset(DATASET_NAME, description="Canvas MCP evaluation dataset")
    else:
        dataset = datasets[0]
    
    # Add examples
    examples = [
        {
            "input": {"query": "List my courses"},
            "output": {"expected_tools": ["canvas_list_courses"]},
        },
        {
            "input": {"query": "What assignments are due this week?"},
            "output": {"expected_tools": ["canvas_get_assignments", "canvas_get_todo"]},
        },
        {
            "input": {"query": "Show my grades for course 58606"},
            "output": {"expected_tools": ["canvas_get_grades"]},
        },
    ]
    
    for example in examples:
        client.create_example(
            inputs=example["input"],
            outputs=example["output"],
            dataset_id=dataset.id,
        )
    
    return dataset


def evaluate_tool_selection(run: Run, example: Example) -> dict:
    """Evaluate if correct tools were selected."""
    expected_tools = example.outputs.get("expected_tools", [])
    # Parse actual tools from run
    actual_tools = []  # Extract from run metadata
    
    correct = set(expected_tools) == set(actual_tools)
    
    return {
        "key": "tool_selection",
        "score": 1.0 if correct else 0.0,
        "comment": f"Expected: {expected_tools}, Got: {actual_tools}",
    }


def run_evaluations():
    """Run all evaluations."""
    dataset = create_evaluation_dataset()
    
    # Define target function (the system under test)
    def target(inputs: dict) -> dict:
        from langchain_canvas import query_canvas
        import asyncio
        result = asyncio.run(query_canvas(inputs["query"]))
        return {"result": result}
    
    # Run evaluation
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[evaluate_tool_selection],
        experiment_prefix="canvas-mcp-eval",
    )
    
    print(f"Evaluation complete. Results: {results}")
    return results


if __name__ == "__main__":
    run_evaluations()
```

---

## GitHub/GitLab Synchronization

### Sync Agent for LangSmith

**`sync_agent_langsmith.py`**:

```python
"""Repository sync agent with LangSmith tracing."""

import os
import subprocess
from dataclasses import dataclass
from langsmith import traceable
import httpx


@dataclass
class SyncConfig:
    """Sync configuration."""
    github_repo: str
    github_token: str
    gitlab_project_path: str
    gitlab_token: str


class LangSmithSyncAgent:
    """Sync agent with LangSmith observability."""
    
    def __init__(self, config: SyncConfig):
        self.config = config
    
    @traceable(name="sync_to_gitlab", run_type="chain")
    def sync_to_gitlab(self, branch: str = "main") -> dict:
        """Sync GitHub to GitLab with tracing."""
        result = {"status": "pending", "branch": branch, "steps": []}
        
        try:
            # Step 1: Fetch from GitHub
            result["steps"].append(self._fetch_github(branch))
            
            # Step 2: Push to GitLab
            result["steps"].append(self._push_gitlab(branch))
            
            result["status"] = "success"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    @traceable(name="fetch_github", run_type="tool")
    def _fetch_github(self, branch: str) -> dict:
        """Fetch latest from GitHub."""
        cmd = ["git", "fetch", "origin", branch]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "step": "fetch_github",
            "success": result.returncode == 0,
            "output": result.stdout,
        }
    
    @traceable(name="push_gitlab", run_type="tool")
    def _push_gitlab(self, branch: str) -> dict:
        """Push to GitLab."""
        gitlab_url = f"https://oauth2:{self.config.gitlab_token}@gitlab.com/{self.config.gitlab_project_path}.git"
        cmd = ["git", "push", gitlab_url, f"{branch}:{branch}", "--force"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "step": "push_gitlab",
            "success": result.returncode == 0,
            "output": result.stdout if result.returncode == 0 else result.stderr,
        }
    
    @traceable(name="check_sync_status", run_type="tool")
    async def check_sync_status(self) -> dict:
        """Check if repos are in sync."""
        async with httpx.AsyncClient() as client:
            # Get GitHub HEAD
            gh_resp = await client.get(
                f"https://api.github.com/repos/{self.config.github_repo}/commits/main",
                headers={"Authorization": f"Bearer {self.config.github_token}"}
            )
            gh_sha = gh_resp.json().get("sha", "")[:7]
            
            # Get GitLab HEAD
            gl_resp = await client.get(
                f"https://gitlab.com/api/v4/projects/{self.config.gitlab_project_path.replace('/', '%2F')}/repository/commits/main",
                headers={"PRIVATE-TOKEN": self.config.gitlab_token}
            )
            gl_sha = gl_resp.json().get("id", "")[:7]
            
            return {
                "github_sha": gh_sha,
                "gitlab_sha": gl_sha,
                "in_sync": gh_sha == gl_sha,
            }
```

---

## Badge Generation

### Badge Types for LangSmith

| Badge | Markdown | Preview |
|-------|----------|---------|
| LangSmith Tracing | `![LangSmith](https://img.shields.io/badge/LangSmith-Enabled-00A67E?logo=langchain)` | ![LangSmith](https://img.shields.io/badge/LangSmith-Enabled-00A67E?logo=langchain) |
| Evaluation Score | `![Eval](https://img.shields.io/badge/Eval%20Score-95%25-brightgreen)` | ![Eval](https://img.shields.io/badge/Eval%20Score-95%25-brightgreen) |
| CI Status | `![CI](https://img.shields.io/github/actions/workflow/status/user/repo/langsmith-ci.yml)` | ![CI](https://img.shields.io/badge/CI-passing-brightgreen) |
| GitLab Sync | `![GitLab](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab)` | ![GitLab](https://img.shields.io/badge/GitLab-Synced-orange?logo=gitlab) |

### Dynamic Badge Generator

**`scripts/generate_langsmith_badges.py`**:

```python
"""Generate LangSmith status badges."""

import json
from pathlib import Path
from langsmith import Client


def get_evaluation_score() -> float:
    """Get latest evaluation score from LangSmith."""
    client = Client()
    
    # Get latest experiment
    experiments = list(client.list_projects(
        project_name_contains="canvas-mcp-eval"
    ))
    
    if not experiments:
        return 0.0
    
    # Calculate average score
    runs = list(client.list_runs(
        project_name=experiments[0].name,
        limit=100,
    ))
    
    if not runs:
        return 0.0
    
    scores = [r.feedback_stats.get("tool_selection", {}).get("avg", 0) for r in runs if r.feedback_stats]
    return sum(scores) / len(scores) if scores else 0.0


def generate_badges(output_dir: Path):
    """Generate all LangSmith badges."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Evaluation score badge
    score = get_evaluation_score()
    color = "brightgreen" if score >= 0.8 else "yellow" if score >= 0.5 else "red"
    
    (output_dir / "eval-score.json").write_text(json.dumps({
        "schemaVersion": 1,
        "label": "Eval Score",
        "message": f"{score*100:.0f}%",
        "color": color,
    }))
    
    # LangSmith enabled badge
    (output_dir / "langsmith.json").write_text(json.dumps({
        "schemaVersion": 1,
        "label": "LangSmith",
        "message": "enabled",
        "color": "00A67E",
    }))
    
    print(f"Generated badges in {output_dir}")


if __name__ == "__main__":
    generate_badges(Path(".github/badges"))
```

---

## Troubleshooting

### Common Issues

**LangSmith traces not appearing:**
```bash
# Verify environment variables
echo $LANGCHAIN_TRACING_V2
echo $LANGCHAIN_API_KEY

# Test connection
python -c "from langsmith import Client; c = Client(); print(list(c.list_projects()))"
```

**GitLab sync authentication failure:**
```bash
# Test GitLab token
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/YOUR_PROJECT_ID"
```

**Evaluation dataset not found:**
```python
from langsmith import Client
client = Client()
# List all datasets
for ds in client.list_datasets():
    print(ds.name)
```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.getLogger("langsmith").setLevel(logging.DEBUG)
```

### LangSmith Dashboard Links

- [Tracing Dashboard](https://smith.langchain.com/projects)
- [Datasets](https://smith.langchain.com/datasets)
- [Evaluations](https://smith.langchain.com/experiments)

---

## Related Documentation

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Canvas LMS MCP Server](../README.md)
- [AutoGen Integration](./AUTOGEN_INTEGRATION.md)
