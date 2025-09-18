FROM python:3.10-slim

WORKDIR /app

# Install build tools for data-collector
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ cmake make \
    python3-dev build-essential \
    pkg-config \
    supervisor \
 && rm -rf /var/lib/apt/lists/*

# --- Build data-collector ---
COPY data-collector/ ./data-collector/
WORKDIR /app/data-collector
RUN mkdir build && cd build && cmake .. && make 
#&& cp data-collector /usr/local/bin/ && cd ../.. && rm -rf data-collector

# --- Install dependencies for local-twin and logging ---
WORKDIR /app
COPY local-twin/ ./local-twin/
COPY logging/ ./logging/

RUN pip install --no-cache-dir -r local-twin/src/requirements.txt \
 && pip install --no-cache-dir -r logging/src/requirements.txt

# --- Supervisor config ---
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /app

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]