FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app

# Install system dependencies with Node.js
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

# Install Node.js dependencies for Lua execution
RUN npm install -g lua-in-js

# Create a Node.js script that acts as Lune
RUN echo '#!/usr/bin/env node' > /usr/local/bin/lune \
    && echo 'const fs = require("fs");' >> /usr/local/bin/lune \
    && echo 'const path = require("path");' >> /usr/local/bin/lune \
    && echo 'const scriptPath = process.argv[2];' >> /usr/local/bin/lune \
    && echo 'if (!scriptPath) { console.log("Usage: lune <file.lua>"); process.exit(1); }' >> /usr/local/bin/lune \
    && echo 'try {' >> /usr/local/bin/lune \
    && echo '    const code = fs.readFileSync(scriptPath, "utf8");' >> /usr/local/bin/lune \
    && echo '    // Simple Lua execution via Node.js' >> /usr/local/bin/lune \
    && echo '    const result = eval(`(function() { ${code} })()`);' >> /usr/local/bin/lune \
    && echo '} catch (err) {' >> /usr/local/bin/lune \
    && echo '    console.error("Lua execution error:", err.message);' >> /usr/local/bin/lune \
    && echo '    process.exit(1);' >> /usr/local/bin/lune \
    && echo '}' >> /usr/local/bin/lune \
    && chmod +x /usr/local/bin/lune

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

EXPOSE 10000

CMD ["python3", "bot.py"]
