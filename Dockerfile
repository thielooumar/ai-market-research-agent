# Dockerfile for B2B Target Scout & Interview Strategist Agent Runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    GOOGLE_GENAI_USE_VERTEXAI=True \
    GOOGLE_CLOUD_PROJECT=keen-optics-296406 \
    GOOGLE_CLOUD_LOCATION=us-east1 \
    PYTHONPATH=/workspace

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & project manifests
COPY pyproject.toml .
COPY README.md .

# Copy source files before installing dependencies
COPY static/ ./static/
COPY app/ ./app/
COPY frontend/ ./frontend/

# Install python dependencies
RUN pip install -e .
# Runtime startup checks – fail fast if imports or static dir are broken
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Bind host to 0.0.0.0 and port 8080 for GCP Agent Engine container health checks
EXPOSE 8080
CMD ["/bin/sh", "/entrypoint.sh"]
