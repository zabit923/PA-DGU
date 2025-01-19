FROM python:3.11-alpine3.16

RUN apk add --no-cache \
    build-base \
    libpq-dev \
    postgresql-dev \
    gcc \
    musl-dev \
    curl \
    bash

RUN pip install --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && chmod +x /root/.local/bin/poetry

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock /src/
WORKDIR /src

RUN poetry install --no-root

COPY ./src /src

EXPOSE 8000

CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload"]
