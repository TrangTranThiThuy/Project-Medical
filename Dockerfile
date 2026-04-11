FROM python:3.13-slim-trixie

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update
# Set working directory
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY pyproject.toml uv.lock ./

# Copier fichiers
COPY pyproject.toml ./
COPY app/migrate_csv_to_mongo.py ./

# Disable dev dependencies (optional but recommended)
#ENV UV_NO_DEV=1

# Install dependencies from lockfile
RUN uv sync --locked

# Copier données
COPY data/ ./data/

# Run migration script
#CMD ["uv", "run", "python", "app/main.py"]

# Commande par défaut
CMD ["uv", "run", "python", "migrate_csv_to_mongo.py", "--csv", "data/healthcare_dataset.csv", "--collection", "Healthcare"]