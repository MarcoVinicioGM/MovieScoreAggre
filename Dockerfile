# Builds the app with the dependencies
FROM python:3.9.18-slim as builder

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install the package in development mode
RUN pip install -e .

# Install test dependencies
RUN pip install pytest pytest-asyncio pytest-mock pytest-cov

# Run tests
RUN python -m pytest tests/test_main.py -v
RUN python -m pytest tests/test_integration.py -v

# Final stage
FROM python:3.9.18-slim

WORKDIR /app

# Copy from builder stage
COPY --from=builder /app .
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Set OMDB API key
ARG OMDB_API_KEY
ENV OMDB_API_KEY=${OMDB_API_KEY}

# Learned that having main sepearated is better for docker
CMD ["python", "run.py"]