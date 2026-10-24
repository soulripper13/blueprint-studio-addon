#!/usr/bin/env bash
set -e

echo "[INFO] Starting Blueprint Studio Supervisor Add-on..."

CONFIG_DIR=""

# 1. Check if user configured a custom workspace directory via options.json
if [ -f "/data/options.json" ]; then
    USER_DIR=$(python3 -c "import json; print(json.load(open('/data/options.json')).get('home_dir', '').strip())" 2>/dev/null || true)
    if [ -n "$USER_DIR" ] && [ -d "$USER_DIR" ]; then
        CONFIG_DIR="$USER_DIR"
        echo "[INFO] Using user-configured workspace directory: ${CONFIG_DIR}"
    elif [ -n "$USER_DIR" ]; then
        echo "[WARN] Configured directory '${USER_DIR}' not found, falling back to defaults"
    fi
fi

# 2. Fall back to standard Home Assistant directories
if [ -z "$CONFIG_DIR" ]; then
    if [ -d "/homeassistant" ]; then
        CONFIG_DIR="/homeassistant"
    elif [ -d "/config" ]; then
        CONFIG_DIR="/config"
    else
        echo "[WARN] Neither /homeassistant nor /config found, creating /homeassistant"
        CONFIG_DIR="/homeassistant"
        mkdir -p /homeassistant
    fi
fi

# 3. Create backwards-compatibility symlink: /config -> $CONFIG_DIR
if [ ! -e "/config" ]; then
    ln -s "$CONFIG_DIR" /config 2>/dev/null || true
fi

# 4. Set HOME environment variable for Git and terminal tools
export HOME="${CONFIG_DIR}"

echo "[INFO] Managing configuration directory: ${CONFIG_DIR}"

exec python3 /app/server.py --port 8099 --config-dir "${CONFIG_DIR}"
