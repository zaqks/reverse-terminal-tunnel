import os
import sys
import time
import threading
import asyncio

# Import our modular components
import components.agent as agent
import components.terminal as terminal


# load env vars
from dotenv import load_dotenv
base_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(base_dir, ".env"))

# ssl
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# --- CONFIGURATION FROM ENVIRONMENT VARS ---
# Simply specify the localhost port + the relay host domain/URL format
PORT = os.getenv("LOCAL_PORT", "8888")
RELAY_HOST_WS = os.getenv("RELAY_HOST_WS", "ws://127.0.0.1:7860")

# Map standard endpoints dynamically based on definitions above
LOCAL_HTTP = f"http://127.0.0.1:{PORT}"
LOCAL_WS = f"ws://127.0.0.1:{PORT}"
SPACE_WS = f"{RELAY_HOST_WS}/ws"


def main():
    print("=" * 50)
    print(" Starting Reverse Terminal Tunnel Orchestrator ")
    print("=" * 50)
    print(f"Target Relay:  {SPACE_WS}")
    print(f"Local Server:  {LOCAL_HTTP}\n")

    # 1. Start the Terminal server in a background daemon thread
    terminal_thread = threading.Thread(
        target=terminal.start_terminal_server, args=(int(PORT),), daemon=True
    )
    terminal_thread.start()

    # Give Tornado a brief moment to bind to the port before launching agent
    time.sleep(1)

    # 2. Initialize the main-thread event loop for the Asyncio Agent
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    agent_task = loop.create_task(agent.start_agent(SPACE_WS, LOCAL_HTTP, LOCAL_WS))

    try:
        loop.run_until_complete(agent_task)
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C detected! Beginning graceful shutdown sequence...")
    finally:
        # 3. Graceful cleanup sequence
        print("[*] Canceling active agent tasks...")
        agent_task.cancel()
        try:
            loop.run_until_complete(agent_task)
        except asyncio.CancelledError:
            pass
        loop.close()

        # Stop Tornado loop & reclaim open PTY descriptors / ports
        terminal.stop_terminal_server()
        print("[+] Ports liberated. Shutdown complete. Goodbye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
