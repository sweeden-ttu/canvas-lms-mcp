# Canvas LMS MCP - RPM/Python/AutoGen/LangSmith/CanvasMCP agents + two worktrees
# Worktree 1: Canvas LMS content retrieval (skeleton/ToC from syllabus)
# Worktree 2: Trustworthy AI presentation-generator (skeleton/ToC from topic)
# Orchestration: hypothesis_generator, evidence_evaluator, CI/CD plan (Mermaid/Markdown),
# log-driven error fixes, Dockerfile/GitHub/GitLab alignment, schema/skeleton/ToC updates.

FROM fedora:39

LABEL maintainer="Scott Weeden <sweeden@ttu.edu>"
LABEL description="Canvas LMS MCP - RPM/Python/AutoGen/LangSmith/agents, two worktrees"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1 \
    LANGCHAIN_TRACING_V2="${LANGCHAIN_TRACING_V2:-false}" \
    LANGCHAIN_PROJECT="${LANGCHAIN_PROJECT:-canvas-lms-mcp-docker}"

# System deps: Python, uv, git (for worktrees), build tools
RUN dnf -y update && \
    dnf -y install \
        python3 \
        python3-devel \
        python3-pip \
        gcc \
        gcc-c++ \
        make \
        openssl-devel \
        libffi-devel \
        curl \
        git \
        ca-certificates \
        && \
    dnf clean all && rm -rf /var/cache/dnf

RUN python3 --version && python3 -m pip --version

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/uv && chmod +x /usr/local/bin/uv

RUN python3 --version && uv --version

WORKDIR /app

# Dependency and project metadata first (cache)
COPY pyproject.toml ./
COPY README.md ./

# Install base + dev + docker (AutoGen, LangSmith) with uv
RUN uv pip install --system -e ".[dev,docker]" 2>/dev/null || \
    uv pip install --system \
        "mcp[cli]>=1.2.0" \
        "httpx>=0.27.0" \
        "python-dotenv>=1.0.0" \
        "pydantic>=2.0.0" \
        "pytest>=8.0.0" \
        "pytest-asyncio>=0.23.0" \
        "autogen-agentchat" \
        "autogen-ext[openai]" \
        "openai>=1.0.0" \
        "langsmith" \
        "langchain"

# Application and agents
COPY config.py ./
COPY server.py ./
COPY generate_spec.py ./
COPY test_hints.json* ./
COPY tests/ ./tests/
COPY agents/ ./agents/
COPY scripts/ ./scripts/
COPY setup-worktree.sh ./

# Two worktree roots (logical workspaces; git worktrees created at runtime if repo is mounted)
ENV WORKTREE_CANVAS="/app/worktrees/canvas-lms-content" \
    WORKTREE_TRUSTWORTHY_AI="/app/worktrees/trustworthy-ai-presentation"

RUN mkdir -p /app/worktrees/canvas-lms-content /app/worktrees/trustworthy-ai-presentation && \
    chmod +x /app/setup-worktree.sh 2>/dev/null || true

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Orchestration entrypoint: run worktrees + CI/CD plan; fallback to server
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh && chown appuser /docker-entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["orchestrate"]
