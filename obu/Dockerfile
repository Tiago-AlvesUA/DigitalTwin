# https://gitlab.es.av.it.pt/its/it2s-itss/-/blob/master/INSTALL.md
FROM ubuntu:24.04

WORKDIR /app

# Add IT2S repo GPG key
RUN apt-get update && apt-get install -y --no-install-recommends gnupg ca-certificates \
 && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B48815023F153A3C

# --- Add IT2S repo and update ---
RUN echo "deb [arch=amd64] https://es.av.it.pt/repo/ubuntu/noble stable main" > /etc/apt/sources.list.d/it2s.list \
 && apt-get update

RUN apt-cache search it2s

# --- Install build tools + IT2S packages ---
RUN apt-get install -y --no-install-recommends \
    gcc g++ cmake make \
    python3 python3.12-venv python3-pip python3-dev build-essential \
    pkg-config supervisor \
    libglib2.0-dev libmbim-glib-dev libqmi-glib-dev libjson-c-dev \
    libcairo2-dev \
    libgirepository1.0-dev gobject-introspection gir1.2-glib-2.0 \
    it2s-itss-git \
 && rm -rf /var/lib/apt/lists/*

#ENV PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/lib/pkgconfig:/usr/share/pkgconfig

# --- Build data-collector ---
COPY data-collector/ ./data-collector/
WORKDIR /app/data-collector
RUN rm -rf build && mkdir build \
 && cd build && cmake .. && make -j$(nproc)
 
# --- Install Python deps ---
WORKDIR /app
COPY local-twin/ ./local-twin/
COPY logging/ ./logging/

RUN python3 -m venv /venv
RUN /venv/bin/pip install --no-cache-dir -r local-twin/src/requirements.txt \
 && /venv/bin/pip install --no-cache-dir -r logging/src/requirements.txt

# --- Supervisor config ---
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /app

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
