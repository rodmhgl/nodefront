# Use official Python runtime based on Alpine Linux
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_ENV=production

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -G appuser

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
RUN apk del gcc musl-dev linux-headers

# Copy application code and configuration
COPY src/app.py ./
COPY src/gunicorn.conf.py ./

# Create necessary directories
RUN mkdir -p /app/share /mnt/secret-store /tmp && \
    chown -R appuser:appuser /app /tmp

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3000

# Health check using production server
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/healthcheck.html?probe=docker', timeout=2)"

# Use Gunicorn for production
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
