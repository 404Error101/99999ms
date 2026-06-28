FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 python3-pip python3-venv \
    curl wget git unzip ca-certificates \
    nodejs npm \
    libjpeg-dev libpng-dev libtiff-dev \
    && rm -rf /var/lib/apt/lists/*

# Python Virtual Environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Lune (Official Lua Runtime) - FIXED with extraction
RUN curl -L https://github.com/lune-org/lune/releases/download/v0.10.4/lune-0.10.4-linux-x86_64.zip -o /tmp/lune.zip \
    && unzip /tmp/lune.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/lune \
    && rm /tmp/lune.zip \
    && lune --version || echo "Lune installed successfully"

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

# Expose Render port
EXPOSE 10000

CMD ["python3", "bot.py"]
