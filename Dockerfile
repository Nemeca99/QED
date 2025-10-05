# QEC Docker Image
# Thin runtime with precomputed slider rays

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy QEC source code
COPY core/ ./core/
COPY research/ ./research/
COPY experiments/ ./experiments/
COPY analysis/ ./analysis/
COPY config/ ./config/
COPY examples/ ./examples/
COPY scripts/ ./scripts/
COPY bench/ ./bench/
COPY setup.py .

# Install QEC package
RUN pip install -e .

# Precompute slider rays at build time
RUN python -c "from core.move_generation_cache import get_move_cache; cache = get_move_cache(); print('Slider rays precomputed')"

# Create logs directory
RUN mkdir -p /logs

# Set environment variables
ENV PYTHONPATH=/app
ENV QEC_LOG_DIR=/logs
ENV QEC_CACHE_DIR=/app/cache

# Create cache directory
RUN mkdir -p /app/cache

# Default command
CMD ["python", "-c", "from core import Game; print('QEC ready!')"]

# Expose logs directory as volume
VOLUME ["/logs"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from core import Game; Game(seed=42); print('Health check passed')" || exit 1
