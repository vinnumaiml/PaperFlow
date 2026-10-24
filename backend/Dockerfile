# PaperFlow Document Processing API & Worker Dockerfile
FROM python:3.12-slim-bookworm

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system document processing binaries and OCR packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ghostscript \
    qpdf \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    libreoffice-writer-nogpu \
    libreoffice-calc-nogpu \
    libreoffice-impress-nogpu \
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Create unprivileged runtime user and data directories
RUN useradd -m -u 1001 paperflow && \
    mkdir -p /app/data/storage /app/data/temp && \
    chown -R paperflow:paperflow /app

USER paperflow

EXPOSE 8000

# Default command: launch FastAPI server with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
