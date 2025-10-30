FROM python:3.14-slim

WORKDIR /app

# System deps (mostly for SSL/certs and debugging)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY app/ /app/


ENV AIRFLOW_BASE_URL=http://host.docker.internal:8080/api/v2
ENV AIRFLOW_USERNAME=admin
ENV AIRFLOW_PASSWORD=admin
ENV MANIFEST_PATH=/app/manifest.json

# Keep stdio unbuffered so MCP clients see streaming
ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "-m", "mcp.app.server"]
