FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md LICENSE alembic.ini ./
COPY alembic ./alembic
COPY apps/api/src ./apps/api/src
COPY pipelines ./pipelines
COPY config ./config
COPY contracts ./contracts

RUN pip install --no-cache-dir .

EXPOSE 8080
CMD ["sh", "-c", "alembic upgrade head && python -m sirta_api.adapters.db.seed && uvicorn sirta_api.entrypoints.main:app --host 0.0.0.0 --port 8080"]
