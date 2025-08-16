FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
  && cp /root/.local/bin/uv /usr/local/bin/uv \
  && chmod 755 /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock* .

RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen || uv sync

ENV PATH="/opt/venv/bin:${PATH}"

COPY . .

RUN adduser --disabled-password appuser \
  && chown -R appuser:appuser /app /opt/venv
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host","0.0.0.0","--port","8000"]