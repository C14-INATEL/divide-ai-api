FROM python:3.12-slim AS base

WORKDIR /app

COPY pyproject.toml .

FROM base AS dev
RUN pip install --no-cache-dir ".[dev]"
COPY . .

FROM base AS prod
RUN pip install --no-cache-dir .
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]