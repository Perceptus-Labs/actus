# Use Python 3.9 slim image for building Lambda package
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ../../src ./src
COPY ../../main.py .
COPY ../../requirements.txt .

# Create deployment package
RUN mkdir -p /package && \
    cp -r /usr/local/lib/python3.9/site-packages/* /package/ && \
    cp -r /build/* /package/ && \
    cd /package && \
    zip -r /lambda-package.zip .

# The package will be available at /lambda-package.zip 