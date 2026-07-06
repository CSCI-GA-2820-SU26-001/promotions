# ======================================================================
# Dockerfile — Promotions Service (Production)
# ======================================================================
FROM python:3.12-slim

# Install system dependencies needed for psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --deploy

# Copy application source
COPY service/ ./service/
COPY wsgi.py .

# Expose the port the app runs on
EXPOSE 8080

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--log-level", "info", "wsgi:app"]