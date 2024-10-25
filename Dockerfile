# Stage 1: Build and test
FROM python:3.9-slim as builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY aggregator/ aggregator/
COPY scrapers/ scrapers/
COPY tests/ tests/
COPY setup.py .

# Run tests
RUN pip install pytest pytest-asyncio
RUN python -m pytest tests/

# Stage 2: Production image
FROM python:3.9-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY aggregator/ aggregator/
COPY scrapers/ scrapers/
COPY setup.py .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Environment variables
ENV OMDB_API_KEY=${OMDB_API_KEY}
ENV SENTRY_DSN=${SENTRY_DSN}

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "aggregator.main:app", "--host", "0.0.0.0", "--port", "8000"]