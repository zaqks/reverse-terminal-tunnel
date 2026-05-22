import asyncio
import websockets
import requests

SPACE_WS = "wss://zaqks-relay.hf.space/ws"
# SPACE_WS = "ws://127.0.0.1:7860/ws"
LOCAL_HTTP = "http://127.0.0.1:8888"
LOCAL_WS = "ws://127.0.0.1:8888"

# Keeps track of active browser-to-tornado socket connections
active_ws_sessions = {}

async def handle_tornado_ws(session_id, path, main_ws):
    """Manages reading messages FROM Tornado and piping them back to the Relay Server."""
    try:
        async with websockets.connect(f"{LOCAL_WS}{path}") as ws:
            active_ws_sessions[session_id] = ws
            while True:
                msg = await ws.recv()
                # Send the incoming data from terminal back up to the relay
                await main_ws.send(f"{session_id}:{msg}")
    except Exception as e:
        print(f"[*] Session {session_id} terminal closed: {e}")
    finally:
        active_ws_sessions.pop(session_id, None)

async def run():
    async with websockets.connect(SPACE_WS, ping_interval=20) as ws:
        await ws.send("local")
        print("[+] Connected to relay")

        while True:
            msg = await ws.recv()
            if ":" not in msg:
                continue

            # Parsing format -> request_id:TYPE:payload
            parts = msg.split(":", 2)
            if len(parts) < 3:
                continue
                
            request_id, msg_type, payload = parts[0], parts[1], parts[2]

            # 1. Handle normal HTTP pages (like index.html)
            if msg_type == "HTTP":
                try:
                    r = requests.get(LOCAL_HTTP + payload)
                    await ws.send(f"{request_id}:{r.text}")
                except Exception as e:
                    await ws.send(f"{request_id}:ERROR {str(e)}")

            # 2. Handle a browser initialization of a Terminal Socket
            elif msg_type == "CONNECT_WS":
                # Fire and forget the asynchronous handler for this socket session
                asyncio.create_task(handle_tornado_ws(request_id, payload, ws))

            # 3. Handle incoming keystrokes from browser to send to Tornado
            elif msg_type == "DATA":
                target_ws = active_ws_sessions.get(request_id)
                if target_ws:
                    await target_ws.send(payload)

            # 4. Handle a closed browser tab
            elif msg_type == "DISCONNECT_WS":
                target_ws = active_ws_sessions.get(request_id)
                if target_ws:
                    await target_ws.close()

asyncio.run(run())