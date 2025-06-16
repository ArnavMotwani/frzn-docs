FROM python:3.11-slim

# system dependencies for psycopg2 and general tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    openssl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install Poetry
RUN pip install --no-cache-dir poetry

# copy only lockfiles so install is cached when code changes
COPY pyproject.toml poetry.lock* README.md /app/

# install runtime deps (no dev, no virtualenv)
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi --no-root

# copy source
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

# migrate then run
ENTRYPOINT ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]