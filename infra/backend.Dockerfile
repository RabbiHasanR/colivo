# syntax=docker/dockerfile:1
# Backend images. Build context: backend/.
#
#   dev  - compose.yaml: the source is bind-mounted and the server reloads.
#   prod - deploys (Phase 9): runtime dependencies only, non-root, no reload.
#
# Both start from the same builder, so dependencies are installed one way.

ARG PYTHON_VERSION=3.12

# ── builder: installs the runtime dependencies into /opt/venv ──────────────
FROM python:${PYTHON_VERSION}-slim AS builder

# uv is only needed to install; it never reaches the final images.
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv

# Precompiled bytecode: a little larger, faster start-up. Use the image's
# Python, never a downloaded one, so the venv works in the runtime stage.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies before the source, so editing code reuses this layer. The
# cache mount keeps uv's download cache out of every image layer. No dev
# tools (pytest, Ruff, pyright): tests run on the host and in CI.
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ── runtime: what both final images share ──────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
EXPOSE 8000

# ── dev: compose.yaml (target: dev) ────────────────────────────────────────
FROM runtime AS dev

# The bind mount in compose.yaml replaces this copy; it lets the image also
# run on its own.
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── prod: deploys (Phase 9) ────────────────────────────────────────────────
FROM runtime AS prod

RUN useradd --system --uid 10001 --no-create-home colivo

COPY . .
# Compile the app's own code at build time; at runtime nothing is written.
RUN python -m compileall -q app

USER colivo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
