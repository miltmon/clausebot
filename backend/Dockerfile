# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# build info (for /buildinfo endpoint)
ARG GIT_SHA=unknown
ARG BUILD_DATE=unknown
RUN echo "REPO=miltmon/clausebot" > /app/buildinfo.txt && \
    echo "SHA=${GIT_SHA}" >> /app/buildinfo.txt && \
    echo "DATE=${BUILD_DATE}" >> /app/buildinfo.txt

# app deps
COPY requirements.txt ./
RUN pip install -U pip && pip install -r requirements.txt

# app code
COPY clausebot_api ./clausebot_api
COPY data ./data
COPY config ./config
COPY pyproject.toml ./
COPY __init__.py ./

# Install package as root before switching user
RUN pip install -e .

# non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# healthcheck for orchestrators that honor it
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s \
  CMD curl -fsS http://127.0.0.1:8081/health || exit 1

EXPOSE 8081
ENV PORT=8081

# uvicorn w/ 2 workers; tweak for CPU
CMD ["uvicorn","clausebot_api.main:app","--host","0.0.0.0","--port","8081","--workers","2"]
