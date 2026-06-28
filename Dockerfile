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


# Install Lune (Official Lua Runtime)
RUN curl -L https://github.com/lune-org/lune/releases/latest/download/lune-linux-x86_64.zip -o lune.zip \
    && unzip lune.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/lune \
    && rm lune.zip

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
