# ==============================================================================
# Base Image: Python 3.12 Slim (Debian Bookworm)
# Slim variant minimizes image attack surface and total size (~150MB vs ~1GB full)
# ==============================================================================
FROM python:3.12-slim

# Prevent Python from writing .pyc files and force unbuffered logging for stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_ENV=production

# Install curl for reliable container HEALTHCHECK and remove apt cache to minimize image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non-privileged system user and group (Principle of Least Privilege)
# Containers should NEVER run as root in production to mitigate container escape exploits
RUN groupadd -r -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -s /sbin/nologin -d /app -c "Container Application User" appuser

# Set application working directory
WORKDIR /app

# Copy dependency specifications first to leverage Docker build cache layers
# (Changes to source code won't trigger re-installation of pip packages)
COPY requirements.txt .

# Install dependencies as root before switching user, without caching wheels
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and assign ownership to non-root user
COPY --chown=appuser:appgroup app/ ./app
COPY --chown=appuser:appgroup wsgi.py .

# Switch to non-root user
USER appuser

# Document that the container listens on port 5000
EXPOSE 5000

# Container-level health check using liveness probe (/healthz)
# Docker marks container as (healthy) or (unhealthy) based on HTTP exit code
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/healthz || exit 1

# Production WSGI process execution using Gunicorn with 2 workers and 2 threads
# Logs streamed directly to stdout/stderr for Docker & log aggregators
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
