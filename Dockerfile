# ---- Base Node ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
# Assuming package.json is there later
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---- Base Python ----
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy python deps
COPY pyproject.toml uv.lock ./
# Install dependencies without installing the project yet (perfect caching)
RUN uv sync --frozen --no-dev --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

# Copy backend and metadata files needed for hatchling build
COPY backend/ ./backend/
COPY README.md ./
# Sync the project itself (non-editable for production)
RUN uv sync --frozen --no-dev --no-editable

# Copy frontend static build
COPY --from=frontend-builder /app/frontend/out /usr/share/nginx/html

# Copy configs
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
