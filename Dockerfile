# Multi-stage Docker build for optimized Manim Animation Agent
# This image pre-installs all system dependencies to eliminate the 2-minute apt-get installation in GitHub Actions
# UPDATED 2025-01-04: Added memvid video-based RAG system support

FROM ubuntu:22.04 as base

# Prevent interactive prompts during apt installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set up basic environment
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    gnupg \
    lsb-release \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add deadsnakes PPA for Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa

# Install all system dependencies in one layer for efficiency
RUN apt-get update && apt-get install -y \
    # Python and development tools
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
    python3-pip \
    build-essential \
    pkg-config \
    git \
    # Graphics and video dependencies  
    libcairo2-dev \
    libgirepository1.0-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    # GraphViz dependencies for pygraphviz
    graphviz \
    libgraphviz-dev \
    graphviz-dev \
    # FFmpeg and multimedia
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    # Audio dependencies
    portaudio19-dev \
    libasound2-dev \
    libsndfile1-dev \
    libfftw3-dev \
    libatlas-base-dev \
    libpulse-dev \
    pulseaudio \
    sox \
    # Image processing
    inkscape \
    imagemagick \
    # LaTeX and document processing
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    texlive-xetex \
    latexmk \
    dvisvgm \
    ghostscript \
    # Additional utilities
    zip \
    unzip \
    tree \
    htop \
    nano \
    vim \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set Python 3.11 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Upgrade pip and install essential Python tools
RUN python3.11 -m pip install --upgrade pip setuptools wheel

# Create a non-root user for better security
RUN useradd -m -s /bin/bash runner && \
    echo 'runner ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set up working directory
WORKDIR /workspace

# Copy requirements file into the image - CRITICAL for baking dependencies
COPY requirements-github-actions.txt /app/requirements-github-actions.txt

# Set TRANSFORMERS_NO_TF env variable before pip install
ENV TRANSFORMERS_NO_TF=1  # Disable TensorFlow integration in transformers

# Install dependencies during the image build process - NO CACHE to ensure clean install
# This eliminates all pip install time from GitHub Actions workflows
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements-github-actions.txt --use-deprecated=legacy-resolver

# Verify critical dependencies are installed during build
RUN python3.11 -c "import manim; print('✅ Manim installed successfully')" && \
    python3.11 -c "import appwrite; print('✅ Appwrite SDK installed successfully')" && \
    python3.11 -c "import numpy, scipy; print('✅ Scientific libraries installed successfully')" && \
    python3.11 -c "import openai, google.generativeai; print('✅ AI libraries installed successfully')" && \
    python3.11 -c "import memvid; print('✅ Memvid video-based RAG installed successfully')" && \
    echo "✅ All core dependencies verified during Docker build"

# Fix ImageMagick policy for PDF handling (common Manim requirement)
RUN sed -i 's/policy domain="coder" rights="none" pattern="PDF"/policy domain="coder" rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml

# Copy Memvid video memory files for documentation RAG system
COPY manim_memory.mp4 /workspace/manim_memory.mp4
COPY manim_memory_index.json /workspace/manim_memory_index.json
COPY manim_memory_index.faiss /workspace/manim_memory_index.faiss

# Set environment variables for optimal performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MANIMCE_USE_PROGRESS_BARS=true
ENV PATH="/home/runner/.local/bin:$PATH"

# Change ownership to runner user (including memvid memory files)
RUN chown -R runner:runner /workspace

# Switch to non-root user
USER runner

# Set up user-specific environment
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Create common directories
RUN mkdir -p /workspace/{output,media,temp_audio,api_outputs}

# Health check to ensure Python and key dependencies work
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3.11 -c "import manim, numpy, cairo, cv2, memvid; print('All dependencies working')" || exit 1

# Default command
CMD ["/bin/bash"]
