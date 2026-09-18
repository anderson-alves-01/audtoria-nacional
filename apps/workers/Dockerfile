FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY apps/workers/src ./apps/workers/src
ENV PYTHONPATH=/app/apps/workers/src
CMD ["python", "-m", "sirta_workers"]
