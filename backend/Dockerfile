# Multi-stage build for minimal image size

FROM python:3.11-slim as builder

WORKDIR /build

# Copy only dependency files first (layer caching)
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir --user .

# ============================================================================

FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app.py .

# Ensure data directory exists
RUN mkdir -p /app/data

# Non-root user for security
RUN useradd -m -u 1000 appuser && \
    cp -r /root/.local /home/appuser/.local && \
    chown -R appuser:appuser /app /home/appuser/.local
USER appuser

# Update PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Run with gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
