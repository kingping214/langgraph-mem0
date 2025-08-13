# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using UV
RUN uv sync --frozen

# Copy application files
COPY main.py example_demo.py CLAUDE.md SECURITY.md docker-entrypoint.sh ./

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Create directories for data and logs
RUN mkdir -p /app/db /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (if needed for future web interface)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["uv", "run", "python", "main.py"]