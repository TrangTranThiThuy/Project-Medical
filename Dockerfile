# Template image to use as a base
FROM ghcr.io/astral-sh/uv:python3.13-trixie

# Set working directory
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies from lockfile
RUN uv sync --locked

# Copy migration script
COPY app/migrate_csv_to_mongo.py ./

# Copy data
COPY data/ ./data/

# Run migration script
CMD ["uv", "run", "python", "migrate_csv_to_mongo.py", "--csv", "data/healthcare_dataset.csv", "--collection", "Healthcare"]