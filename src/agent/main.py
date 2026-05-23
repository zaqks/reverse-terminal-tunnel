import os
import sys
import time
import threading
import asyncio
import argparse

# Import our modular components
import components.agent as agent
import components.terminal as terminal

import certifi


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reverse Terminal Tunnel Orchestrator"
    )

    parser.add_argument(
        "--local-port",
        type=int,
        required=True,
        help="Local server port (e.g. 8888)",
    )

    parser.add_argument(
        "--relay-host-ws",
        type=str,
        required=True,
        help="Relay WebSocket base URL (e.g. ws://127.0.0.1:7860)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # ssl
    os.environ["SSL_CERT_FILE"] = certifi.where()
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    PORT = args.local_port
    RELAY_HOST_WS = args.relay_host_ws

    # Map endpoints
    LOCAL_HTTP = f"http://127.0.0.1:{PORT}"
    LOCAL_WS = f"ws://127.0.0.1:{PORT}"
    SPACE_WS = f"{RELAY_HOST_WS}/ws"

    print("=" * 50)
    print(" Starting Reverse Terminal Tunnel Orchestrator ")
    print("=" * 50)
    print(f"Target Relay:  {SPACE_WS}")
    print(f"Local Server:  {LOCAL_HTTP}\n")

    # 1. Start the Terminal server in a background daemon thread
    terminal_thread = threading.Thread(
        target=terminal.start_terminal_server,
        args=(PORT,),
        daemon=True
    )
    terminal_thread.start()

    # Give server a moment to bind
    time.sleep(1)

    # 2. Async agent loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    agent_task = loop.create_task(
        agent.start_agent(SPACE_WS, LOCAL_HTTP, LOCAL_WS)
    )

    try:
        loop.run_until_complete(agent_task)
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C detected! Beginning graceful shutdown sequence...")
    finally:
        print("[*] Canceling active agent tasks...")
        agent_task.cancel()

        try:
            loop.run_until_complete(agent_task)
        except asyncio.CancelledError:
            pass

        loop.close()

        # Cleanup terminal server
        terminal.stop_terminal_server()

        print("[+] Ports liberated. Shutdown complete. Goodbye.")
        sys.exit(0)


if __name__ == "__main__":
    main()