#!/bin/bash

set -e

# Go to script directory
# cd "$(dirname "$0")"

echo "Starting FRPC..."

# Stop any existing frpc process (optional but useful)
pkill frpc 2>/dev/null || true

# Start FRPC in background using TOML config
# nohup ./frpc -c ./frpc.toml > frpc.log 2>&1 &

# echo "FRPC started successfully."
# echo "Log file: frpc.log"
# echo "PID: $!"

./frpc -c ./frpc.toml

