# Template image to use as a base
FROM ghcr.io/astral-sh/uv:python3.13-trixie

# Set working directory
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY pyproject.toml uv.lock ./

# Copy migration script
COPY app/migrate_csv_to_mongo.py ./

# Install dependencies from lockfile
RUN uv sync --frozen

# The CSV data is mounted via volume in docker-compose at runtime
# A non-root user is created to improve security
# Root containers can be dangerous if vulnerabilities exist
RUN addgroup --system appgroup && adduser --system --no-create-home --disabled-login --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
ENV HOME=/app
ENV UV_CACHE_DIR=/app/.cache/uv
USER appuser

# Healthcheck to verify that the container is working correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import sys; sys.exit(0)" || exit 1

# Run migration script
CMD ["uv", "run", "python", "migrate_csv_to_mongo.py", "--csv", "data/healthcare_dataset.csv", "--collection", "Healthcare"]
