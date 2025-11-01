# Python Agent Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies needed by agents
RUN pip install --no-cache-dir qdrant-client pillow aiohttp

# Copy agent code
COPY . .

# Copy data directories (if needed at runtime)
# Note: In production, these should be mounted as volumes or loaded from S3
# COPY ../inventory_data ./inventory_data

# Create a non-root user
RUN useradd -m -u 1001 agentuser && chown -R agentuser:agentuser /app
USER agentuser

# Expose agent port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the agent
CMD ["python", "agent.py"]
