# --- Stage 1: Build dependencies & package ---
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install C build toolchain required for psycopg2 and other native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 1. Create virtual environment
RUN uv venv /opt/venv

# 2. Copy project files (metadata, root main.py, and src directory)
COPY pyproject.toml README.md* main.py ./
COPY src/ src/

# 3. Install project dependencies and local wheel directly using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install gunicorn .


# --- Stage 2: Final minimal runtime ---
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install runtime PostgreSQL client library
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy rest of application source code
COPY . .

# Create and switch to a non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Since main.py is in the root directory, point uvicorn to main:app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]