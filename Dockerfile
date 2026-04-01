FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY test_server.py .

# Set environment variables
ENV SANDBOX_API_KEY=key_test_ed6b10d21cf546d7b4b600021f91c341
ENV SANDBOX_API_SECRET=secret_test_798d3274325741fab93dd24bbb786a3a
ENV SANDBOX_API_URL=https://api.sandbox.co.in
ENV SANDBOX_API_VERSION=1.0.0
ENV LOG_LEVEL=INFO

# Expose port (if needed for monitoring)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the server
CMD ["python", "server.py"]
