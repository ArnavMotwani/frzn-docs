FROM python:3.11-alpine

RUN apk add --no-cache libpq openssl git

WORKDIR /app

# Install system dependencies for psycopg2
RUN apk add --no-cache libpq openssl

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files and README (required by poetry if referenced in pyproject.toml)
COPY pyproject.toml poetry.lock* README.md /app/

# Install dependencies (not dev, don't install as a package)
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi --no-root

# Copy app source and migrations
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

# Migrate & run FastAPI app
ENTRYPOINT ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]