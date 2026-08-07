# Use a lightweight python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if any are needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY server/ ./server/
COPY static/ ./static/
COPY data/ ./data/

# Expose server port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run uvicorn server
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
