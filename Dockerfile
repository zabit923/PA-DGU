FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY src /app

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--reload"]
