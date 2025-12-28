# Use a slim version of Python 3.12 for a small, secure footprint
FROM python:3.12-slim

# Set environment variables to optimize Python for containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-privileged user for security
RUN useradd -m appuser
USER appuser

# Chainlit default port
EXPOSE 8000

# Healthcheck to monitor the status of the web server
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Launch the application using Chainlit
CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
