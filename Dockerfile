FROM python:3.11.11-alpine3.19

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update

# Базовые инструменты сборки
RUN apk add --no-cache gcc || echo "gcc failed"
RUN apk add --no-cache musl-dev || echo "musl-dev failed"

# PostgreSQL пакеты
RUN apk add --no-cache postgresql-dev || echo "postgresql-dev failed"
RUN apk add --no-cache postgresql-client || echo "postgresql-client failed"

# Дополнительные утилиты
RUN apk add --no-cache poppler-utils || echo "poppler-utils failed"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 8000

COPY . /usr/src/app/
COPY . /usr/src/admin/

ENV UV_HTTP_TIMEOUT=60
RUN uv sync --frozen --no-cache

RUN chmod +x /usr/src/app/docker-entrypoint.sh

ENTRYPOINT ["sh", "/usr/src/app/docker-entrypoint.sh"]
