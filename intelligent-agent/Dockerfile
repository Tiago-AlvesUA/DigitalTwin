FROM python:3.10-slim

WORKDIR /app

# Install build dependencies for pyquadkey2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy src code
COPY src/ .

# First run the video stream, because agent depends on it
CMD ["bash", "-c", "python mjpeg_stream.py & sleep 5 && python agent.py"]