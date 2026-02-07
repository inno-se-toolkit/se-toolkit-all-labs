FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install autochecker deps (cached layer)
COPY autochecker/requirements.txt /app/autochecker/requirements.txt
RUN pip install --no-cache-dir -r /app/autochecker/requirements.txt

# Install bot deps (cached layer)
COPY tg_bot_autochecker/requirements.txt /app/tg_bot_autochecker/requirements.txt
RUN pip install --no-cache-dir -r /app/tg_bot_autochecker/requirements.txt

# Copy source
COPY autochecker/ /app/autochecker/
COPY tg_bot_autochecker/ /app/tg_bot_autochecker/

# Create directories for runtime data
RUN mkdir -p /app/autochecker/results /app/data

WORKDIR /app/tg_bot_autochecker
