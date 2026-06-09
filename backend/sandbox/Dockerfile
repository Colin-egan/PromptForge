# CadQuery Sandbox - Isolated execution environment for untrusted code
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for CadQuery
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    cadquery==2.4.0 \
    cadquery-ocp==7.7.2 \
    trimesh==4.0.5 \
    numpy-stl==3.1.1 \
    pygltflib==1.16.1

# Create output directory
RUN mkdir -p /output && chmod 777 /output

# Copy executor script
COPY executor.py /app/executor.py

# Create non-root user for security
RUN useradd -m -u 1000 sandbox && \
    chown -R sandbox:sandbox /app /output

# Switch to non-root user
USER sandbox

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command (will be overridden)
CMD ["python", "executor.py"]

# Made with Bob
