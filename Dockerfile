# Use Fedora 39 (RPM-based) as base image
# Fedora 39 includes Python 3.12, which meets the >=3.10 requirement
# Alternative: Use Rocky Linux 9 and install Python 3.11+ from EPEL or build from source
FROM fedora:39

# Set maintainer
LABEL maintainer="Scott Weeden <sweeden@ttu.edu>"
LABEL description="Canvas LMS MCP Server - RPM-based container"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies required for Python and uv
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
    dnf clean all && \
    rm -rf /var/cache/dnf

# Verify Python version (should be 3.12+ on Fedora 39)
RUN python3 --version && python3 -m pip --version

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv

# Verify installations
RUN python3 --version && \
    uv --version

# Create app directory
WORKDIR /app

# Copy dependency files first (for better layer caching)
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies using uv
RUN uv pip install --system \
    "mcp[cli]>=1.2.0" \
    "httpx>=0.27.0" \
    "python-dotenv>=1.0.0" \
    "pydantic>=2.0.0"

# Copy project files
COPY config.py ./
COPY server.py ./
COPY generate_spec.py ./
COPY test_hints.json* ./

# Copy tests directory (comment out if tests/ doesn't exist)
COPY tests/ ./tests/

# Set up non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port for HTTP transport (if used)
EXPOSE 8000

# Default command - run server with stdio transport
CMD ["python3", "server.py"]

# For HTTP transport debugging, use:
# CMD ["python3", "server.py", "--transport", "streamable-http", "--port", "8000"]
