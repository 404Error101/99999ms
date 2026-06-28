FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app

# Install system dependencies including Lua for Lune
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 python3-pip python3-venv \
    curl wget git unzip ca-certificates \
    nodejs npm \
    libjpeg-dev libpng-dev libtiff-dev \
    lua5.3 \
    && rm -rf /var/lib/apt/lists/*

# Python Virtual Environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages - ADDED joblib explicitly
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt joblib

# Install Lune v0.10.4 from the specific URL
RUN echo "Installing Lune v0.10.4..." \
    && curl -L https://github.com/lune-org/lune/releases/download/v0.10.4/lune-0.10.4-linux-x86_64.zip -o /tmp/lune.zip \
    && unzip /tmp/lune.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/lune \
    && rm /tmp/lune.zip \
    && lune --version || echo "Lune installed"

# CRITICAL FIX: Create mock exec_env module for Lune
RUN mkdir -p /usr/local/lib/lua/5.3 \
    && echo 'return { env = os.getenv, args = {...} }' > /usr/local/lib/lua/5.3/exec_env.lua

ENV LUA_PATH="/usr/local/lib/lua/5.3/?.lua;;"

# Copy bot files
COPY . /app/

# Create necessary directories
RUN mkdir -p \
    dumps/original \
    dumps/dumped \
    dumps/beautify \
    dumps/decompile \
    unobfuscated \
    obfuscated \
    deobfuscate/.in \
    deobfuscate/.out \
    medal51 \
    && chmod -R 777 /app

# PORT BINDING FIX: Ensure the app binds to 0.0.0.0
EXPOSE 10000

# Use a start command that explicitly binds to all interfaces
CMD ["sh", "-c", "python3 -m pip install joblib && python3 bot.py --host 0.0.0.0 --port ${PORT}"]
