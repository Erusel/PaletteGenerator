# PNG Recoloring Tool - Streamlit Web Application
# Multi-stage build for optimized image size

# ============================================
# Stage 1: Base image with Python
# ============================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# ============================================
# Stage 2: Builder stage for dependencies
# ============================================
FROM base as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# ============================================
# Stage 3: Production image
# ============================================
FROM base as production

# Create non-root user for security
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -m appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Update PATH to include user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application files
COPY --chown=appuser:appuser palettes.py .
COPY --chown=appuser:appuser recolor.py .
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser main.py .

# Create directories for assets and generated files
RUN mkdir -p /app/assets /app/generated \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Streamlit default port
EXPOSE 8501

# Configure Streamlit
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE=light

# Run Streamlit app
CMD ["streamlit", "run", "app.py"]