# Reverse Terminal Tunnel (RTT)

A lightweight, secure reverse terminal architecture that lets you access your local machine's terminal from anywhere in the world—without raw TCP tunneling or port forwarding.

Unlike traditional SSH or raw TCP tunnels (like Ngrok), this project relies strictly on HTTP and WebSockets multiplexed over an application layer. This makes it incredibly resilient against strict firewalls that block standard SSH ports or non-HTTP traffic.

---

## How It Works

The architecture consists of three components:

1. **The Relay (`relay.py`)**: A publicly hosted FastAPI server. It acts as the central router, bridging connections between the browser client and your local agent.
2. **The Agent (`main.py`, `agent.py`, `terminal.py`)**: Runs on your target/local machine. It starts a local Unix bash terminal session (via Tornado/Terminado) and establishes an outbound persistent WebSocket connection to the Relay.
3. **The Web Client (`index.html`)**: A frontend UI using `xterm.js`. You open it anywhere, type in your Relay's URL, and get a fully interactive, responsive bash prompt inside your browser.

---

## Architecture Overview

```text
  [ Local Machine ]                      [ Public Cloud ]              [ Remote Device ]
+--------------------+                 +------------------+          +-------------------+
|  Tornado (Bash)    |                 |                  |          |                   |
|         ^          |                 |                  |          |                   |
|         v          |  Outbound WS    |                  |  WS/HTTP |                   |
|    Local Agent     |================>|   FastAPI Relay  |<=========|   Browser Client  |
|     (main.py)      |                 |    (relay.py)    |          |   (index.html)    |
+--------------------+                 +------------------+          +-------------------+

```

---

## Quick Start (Instant Demo)

If you want to test the ecosystem immediately without hosting your own infrastructure, you can use the pre-configured live services.

### 1. Launch the Agent on your Machine

Run this single-line command on your local machine to automatically provision, configure, and connect an agent to the live public relay hosted on Hugging Face Spaces:

```bash
wget -O- https://github.com/zaqks/remote-command-execution-interface/blob/main/src/utils/inject.sh | sh

```

### 2. Access your Terminal via the Web Client

1. Navigate to the hosted Web Client: `https://zaqks.github.io/remote-command-execution-interface/`
2. In the host prompt overlay, input the target relay server URL: `https://zaqks-relay.hf.spaces`
3. Click **Start** to open your real-time browser-based terminal session.

---

## Custom Deployment Guide

If you prefer to run the entire stack on your own infrastructure, follow these steps:

### Step 1: Host the Relay Server

Deploy `relay.py` onto any publicly accessible server (e.g., AWS, DigitalOcean, Heroku, or Hugging Face Spaces), no VPS required.

---

### Step 2: Run the Agent on your Target Machine

On the local computer you want to access remotely, execute the orchestrator.

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Connect your local terminal to your relay
python main.py --local-port 8888 --relay-host-ws wss://YOUR_RELAY_DOMAIN

```

---

### Step 3: Access your Terminal from Anywhere

1. Open `index.html` in any browser (you can double-click it locally, or host it on GitHub Pages).
2. Enter your custom Relay server URL (e.g., `https://YOUR_RELAY_DOMAIN`) in the host prompt overlay.
3. Click **Start** to spawn a fully functional, real-time terminal shell.

---

## Security Notice

> [!WARNING]
> This setup allows unrestricted root/user bash terminal execution via a public endpoint for demonstration purposes. In production environments, ensure you add authentication layers.