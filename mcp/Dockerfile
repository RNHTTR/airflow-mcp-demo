FROM python:3.14-slim

WORKDIR /mcp

# System deps (mostly for SSL/certs and debugging)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from mcp/ directory
COPY . /mcp/

ENV AIRFLOW_BASE_URL=http://host.docker.internal:8080/api/v2
ENV AIRFLOW_USERNAME=admin
ENV AIRFLOW_PASSWORD=admin
ENV MANIFEST_PATH=/mcp/manifest.json
ENV PYTHONPATH=/mcp


# Expose the SSE port
EXPOSE 8000

CMD ["python", "-u", "app/server.py"]