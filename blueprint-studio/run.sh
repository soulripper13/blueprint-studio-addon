#!/usr/bin/env bash
set -e

echo "[INFO] Starting Blueprint Studio Supervisor Add-on..."

# Home Assistant Supervisor mounts `homeassistant_config:rw` to `/homeassistant`
CONFIG_DIR=""
if [ -d "/homeassistant" ]; then
    CONFIG_DIR="/homeassistant"
elif [ -d "/config" ]; then
    CONFIG_DIR="/config"
else
    echo "[WARN] Neither /homeassistant nor /config found, creating /homeassistant"
    CONFIG_DIR="/homeassistant"
    mkdir -p /homeassistant
fi

# Create backwards-compatibility symlink: /config -> /homeassistant
if [ ! -e "/config" ]; then
    ln -s "$CONFIG_DIR" /config 2>/dev/null || true
fi

export HOME="${CONFIG_DIR}"

echo "[INFO] Managing configuration directory: ${CONFIG_DIR}"

exec python3 /app/server.py --port 8099 --config-dir "${CONFIG_DIR}"
