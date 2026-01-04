FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt /app/backend_requirements.txt
RUN pip install --no-cache-dir -r /app/backend_requirements.txt

# Install ccxt for trading
RUN pip install --no-cache-dir ccxt

# Copy backend app (needed for imports)
COPY backend/app /app/backend/app

# Copy worker code
COPY worker/worker.py /app/worker.py

# Run the worker
CMD ["python", "worker.py"]
