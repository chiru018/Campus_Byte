# ============================================================
# Campus Byte FastAPI Backend — Production Dockerfile
# ============================================================
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure Linux LF line endings and execution permissions on entrypoint script
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Expose FastAPI backend port
EXPOSE 8000

# Run migrations, seed verification, then start uvicorn
CMD ["./entrypoint.sh"]
