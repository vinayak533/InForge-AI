# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source code and build it
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the Python backend and assemble the application
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for better Docker layering and caching
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the built frontend static files from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy the rest of the backend files
COPY backend/ ./backend/

# Set up runtime user and permissions (required for Hugging Face Spaces non-root user)
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

# Switch to the non-root user
USER user

# Set standard environment variables for FastAPI and Hugging Face
ENV PORT=7860
ENV HOST=0.0.0.0
ENV ENV=production
# Add app/backend to python path so module resolution works seamlessly
ENV PYTHONPATH=/app/backend

# Hugging Face Spaces defaults to exposing port 7860
EXPOSE 7860

# Command to run the application (running main.py as a module)
CMD ["python", "backend/main.py"]
