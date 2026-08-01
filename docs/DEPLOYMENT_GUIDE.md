# Production Deployment & Containerization Guide

## 1. Overview
This guide provides instructions for deploying the **MONEYYYYYY** backend platform using Docker, Gunicorn/Uvicorn workers, and Google Cloud Run / Kubernetes (GKE).

---

## 2. Dockerfile Build & Execution

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY packages/ ./packages/
RUN pip install --no-cache-dir . uvicorn gunicorn

ENV ENVIRONMENT=production
EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "packages.api.main:app"]
```

---

## 3. Environment Variables for Production
Set the following mandatory secrets in your deployment environment:
- `ENVIRONMENT=production`
- `OPENBB_API_KEY=<your-production-openbb-key>`
- `GEMINI_API_KEY=<your-production-gemini-key>`
- `LOG_LEVEL=INFO`
