# LILITH ETERNAL - Docker Image
# Standalone uncensored AI companion with local Ollama

FROM python:3.11-slim

LABEL maintainer="LuciferOS"
LABEL description="LILITH ETERNAL - Free Uncensored AI Companion"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY lilith_server.py .
COPY static/ ./static/ 2>/dev/null || true

# Environment variables
ENV OLLAMA_URL=http://ollama:11434
ENV OLLAMA_MODEL=dolphin-mistral:7b
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application
CMD ["python", "lilith_server.py"]
