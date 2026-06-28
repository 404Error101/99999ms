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
    lua5.3 \
    && rm -rf /var/lib/apt/lists/*

# Python Virtual Environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Lune properly
RUN curl -L https://github.com/lune-org/lune/releases/download/v0.10.4/lune-0.10.4-linux-x86_64.zip -o /tmp/lune.zip \
    && unzip /tmp/lune.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/lune \
    && rm /tmp/lune.zip

# CRITICAL FIX: Create a wrapper that properly handles 'lune run'
RUN echo '#!/bin/bash' > /usr/local/bin/lune-wrapper \
    && echo '' >> /usr/local/bin/lune-wrapper \
    && echo '# Parse arguments' >> /usr/local/bin/lune-wrapper \
    && echo 'ARGS=("$@")' >> /usr/local/bin/lune-wrapper \
    && echo 'SCRIPT_FILE=""' >> /usr/local/bin/lune-wrapper \
    && echo '' >> /usr/local/bin/lune-wrapper \
    && echo '# Handle "run" command' >> /usr/local/bin/lune-wrapper \
    && echo 'if [[ "${ARGS[0]}" == "run" ]]; then' >> /usr/local/bin/lune-wrapper \
    && echo '    SCRIPT_FILE="${ARGS[1]}"' >> /usr/local/bin/lune-wrapper \
    && echo '    shift 2' >> /usr/local/bin/lune-wrapper \
    && echo 'else' >> /usr/local/bin/lune-wrapper \
    && echo '    SCRIPT_FILE="${ARGS[0]}"' >> /usr/local/bin/lune-wrapper \
    && echo '    shift 1' >> /usr/local/bin/lune-wrapper \
    && echo 'fi' >> /usr/local/bin/lune-wrapper \
    && echo '' >> /usr/local/bin/lune-wrapper \
    && echo '# Check if file exists' >> /usr/local/bin/lune-wrapper \
    && echo 'if [[ ! -f "$SCRIPT_FILE" ]]; then' >> /usr/local/bin/lune-wrapper \
    && echo '    echo "Error: File not found: $SCRIPT_FILE"' >> /usr/local/bin/lune-wrapper \
    && echo '    exit 1' >> /usr/local/bin/lune-wrapper \
    && echo 'fi' >> /usr/local/bin/lune-wrapper \
    && echo '' >> /usr/local/bin/lune-wrapper \
    && echo '# Create a mock exec_env module and run the script' >> /usr/local/bin/lune-wrapper \
    && echo 'lua -e "' >> /usr/local/bin/lune-wrapper \
    && echo '  local args = {...}' >> /usr/local/bin/lune-wrapper \
    && echo '  local script_file = args[1]' >> /usr/local/bin/lune-wrapper \
    && echo '  table.remove(args, 1)' >> /usr/local/bin/lune-wrapper \
    && echo '  ' >> /usr/local/bin/lune-wrapper \
    && echo '  -- Mock exec_env' >> /usr/local/bin/lune-wrapper \
    && echo '  _G.exec_env = {' >> /usr/local/bin/lune-wrapper \
    && echo '    env = function(name) return os.getenv(name) end,' >> /usr/local/bin/lune-wrapper \
    && echo '    args = args,' >> /usr/local/bin/lune-wrapper \
    && echo '    platform = "linux",' >> /usr/local/bin/lune-wrapper \
    && echo '    arch = "x86_64"' >> /usr/local/bin/lune-wrapper \
    && echo '  }' >> /usr/local/bin/lune-wrapper \
    && echo '  ' >> /usr/local/bin/lune-wrapper \
    && echo '  -- Override require to handle exec_env' >> /usr/local/bin/lune-wrapper \
    && echo '  local original_require = require' >> /usr/local/bin/lune-wrapper \
    && echo '  function require(path)' >> /usr/local/bin/lune-wrapper \
    && echo '    if path == "exec_env" then' >> /usr/local/bin/lune-wrapper \
    && echo '      return _G.exec_env' >> /usr/local/bin/lune-wrapper \
    && echo '    end' >> /usr/local/bin/lune-wrapper \
    && echo '    return original_require(path)' >> /usr/local/bin/lune-wrapper \
    && echo '  end' >> /usr/local/bin/lune-wrapper \
    && echo '  ' >> /usr/local/bin/lune-wrapper \
    && echo '  -- Execute the script' >> /usr/local/bin/lune-wrapper \
    && echo '  local file = io.open(script_file, "r")' >> /usr/local/bin/lune-wrapper \
    && echo '  if not file then' >> /usr/local/bin/lune-wrapper \
    && echo '    print("Error: Cannot open file:", script_file)' >> /usr/local/bin/lune-wrapper \
    && echo '    os.exit(1)' >> /usr/local/bin/lune-wrapper \
    && echo '  end' >> /usr/local/bin/lune-wrapper \
    && echo '  local code = file:read("*a")' >> /usr/local/bin/lune-wrapper \
    && echo '  file:close()' >> /usr/local/bin/lune-wrapper \
    && echo '  ' >> /usr/local/bin/lune-wrapper \
    && echo '  local fn, err = loadstring(code, script_file)' >> /usr/local/bin/lune-wrapper \
    && echo '  if not fn then' >> /usr/local/bin/lune-wrapper \
    && echo '    print("Error loading script:", err)' >> /usr/local/bin/lune-wrapper \
    && echo '    os.exit(1)' >> /usr/local/bin/lune-wrapper \
    && echo '  end' >> /usr/local/bin/lune-wrapper \
    && echo '  ' >> /usr/local/bin/lune-wrapper \
    && echo '  local success, result = pcall(fn)' >> /usr/local/bin/lune-wrapper \
    && echo '  if not success then' >> /usr/local/bin/lune-wrapper \
    && echo '    print("Error executing script:", result)' >> /usr/local/bin/lune-wrapper \
    && echo '    os.exit(1)' >> /usr/local/bin/lune-wrapper \
    && echo '  end' >> /usr/local/bin/lune-wrapper \
    && echo '" "$SCRIPT_FILE" "$@"' >> /usr/local/bin/lune-wrapper \
    && chmod +x /usr/local/bin/lune-wrapper

# Replace the lune binary with our wrapper
RUN mv /usr/local/bin/lune /usr/local/bin/lune-real \
    && ln -sf /usr/local/bin/lune-wrapper /usr/local/bin/lune

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
