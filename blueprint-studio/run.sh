#!/usr/bin/env bash
set -e

echo "[INFO] Starting Blueprint Studio Supervisor Add-on..."

CONFIG_DIR="/config"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "[WARN] /config directory not found, fallback to /app"
    CONFIG_DIR="/app"
fi

echo "[INFO] Managing configuration directory: ${CONFIG_DIR}"

exec python3 /app/server.py --port 8099 --config-dir "${CONFIG_DIR}"
