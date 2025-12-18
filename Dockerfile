# Use official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies (FFmpeg is required for yt-dlp merging)
RUN apt-get update && apt-get install -y ffmpeg git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (Render sets PORT env var)
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]
