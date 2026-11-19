# Development image for the backend (compose.yaml). Build context: backend/.
# A production image (no reload, non-root, no dev dependencies) comes in Phase 9.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /bin/

# The venv lives outside /app so the source bind mount in compose.yaml
# doesn't hide it. No bytecode is written, so the container never leaves
# root-owned __pycache__ folders in the bind-mounted source.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependencies first, so editing the source doesn't reinstall them.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
