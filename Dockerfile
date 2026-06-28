FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app

# Install system dependencies with Lua
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 python3-pip python3-venv \
    curl wget git unzip ca-certificates \
    nodejs npm \
    libjpeg-dev libpng-dev libtiff-dev \
    lua5.3 lua5.3-dev luarocks \
    && rm -rf /var/lib/apt/lists/*

# Python Virtual Environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Lune properly
RUN echo "Installing Lune..." \
    && curl -L https://github.com/lune-org/lune/releases/download/v0.10.4/lune-0.10.4-linux-x86_64.zip -o /tmp/lune.zip \
    && unzip -o /tmp/lune.zip -d /tmp/lune_extract/ \
    && cp /tmp/lune_extract/lune /usr/local/bin/ \
    && chmod +x /usr/local/bin/lune \
    && rm -rf /tmp/lune.zip /tmp/lune_extract \
    && echo "Lune installed successfully"

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

# Fix Lune module resolution with environment
ENV LUNE_MODULE_PATH="/app:/usr/local/lib/lua/5.3:/usr/local/share/lua/5.3"

# Expose Render port
EXPOSE 10000

# Run with debug output
CMD ["sh", "-c", "echo 'Starting bot with Lune support...' && python3 -u bot.py 2>&1 | tee /app/log.txt"]
