# ===== Build Stage =====
FROM python:3.12-slim AS builder

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using uv with optimizations
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy source code
COPY src/ ./src/

# Install the package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ===== Runtime Stage =====
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy Python environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY --from=builder /app/src /app/src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create and use non-root user
RUN groupadd --system --gid 1000 nonroot && \
    useradd --system --uid 1000 --gid nonroot --home /home/nonroot nonroot && \
    mkdir -p /home/nonroot && \
    chown -R nonroot:nonroot /home/nonroot /app

USER nonroot

# Expose port (Cloud Run will provide PORT env var)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Start the FastAPI application using server.py which reads PORT env var
CMD ["/app/.venv/bin/python", "-m", "detector.server"]
