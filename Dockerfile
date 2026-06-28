FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    ca-certificates \
    nodejs \
    npm \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p \
    dumps/original \
    dumps/dumped \
    dumps/beautify \
    dumps/decompile \
    unobfuscated \
    obfuscated \
    deobfuscate/.in \
    deobfuscate/.out \
    medal51

RUN chmod -R 755 /app

EXPOSE 10000

CMD ["python3", "bot.py"]
