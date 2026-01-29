FROM python:3.11-slim

# System deps (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/german-data-job-analyzer

# Good defaults
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1