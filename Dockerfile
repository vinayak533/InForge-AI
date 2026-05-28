FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (curl for healthchecks, build-essential for packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install them
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Create a non-root user with UID 1000 (required for Hugging Face Spaces)
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

# Switch to the non-root user
USER user

# Set environment variables for production
ENV PORT=7860
ENV HOST=0.0.0.0
ENV ENV=production
ENV PYTHONPATH=/app/backend

# Expose Hugging Face's default port
EXPOSE 7860

# Run the FastAPI server using main.py
CMD ["python", "backend/main.py"]
