# syntax=docker/dockerfile:1

# Cài dependencies riêng một tầng để sửa code không phải cài lại.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS deps

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project


FROM python:3.14-slim-bookworm AS runtime

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=deps /app/.venv /app/.venv
COPY app ./app

RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Không bật --reload: đây là ảnh chạy thật, không phải môi trường dev.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
