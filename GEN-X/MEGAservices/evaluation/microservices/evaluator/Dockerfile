FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create directories
RUN mkdir -p /app/data/uploads /app/data/results /app/logs

# Set Python path
ENV PYTHONPATH=/app/src

# Expose HTTP port
EXPOSE 8000

# Run the FastAPI server
CMD ["python", "src/main.py"]
