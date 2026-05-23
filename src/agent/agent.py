import asyncio
import websockets
import requests

# Track active session sockets globally within the agent context
active_ws_sessions = {}

async def handle_tornado_ws(session_id, path, main_ws, local_ws):
    """Manages reading messages FROM Tornado and piping them back to the Relay Server."""
    try:
        async with websockets.connect(f"{local_ws}{path}") as ws:
            active_ws_sessions[session_id] = ws
            while True:
                msg = await ws.recv()
                await main_ws.send(f"{session_id}:{msg}")
    except Exception as e:
        pass  # Fail silently when backend terminal closes or disconnects
    finally:
        active_ws_sessions.pop(session_id, None)

async def start_agent(space_ws, local_http, local_ws):
    """Main agent loop connecting to the external relay."""
    try:
        async with websockets.connect(space_ws, ping_interval=20) as ws:
            await ws.send("local")
            print("[+] Agent successfully connected to external relay")

            while True:
                msg = await ws.recv()
                if ":" not in msg:
                    continue

                parts = msg.split(":", 2)
                if len(parts) < 3:
                    continue
                    
                request_id, msg_type, payload = parts[0], parts[1], parts[2]

                # 1. Handle standard HTTP routing
                if msg_type == "HTTP":
                    try:
                        # Use a short timeout to prevent hanging the main loop if backend delays
                        r = requests.get(local_http + payload, timeout=5)
                        await ws.send(f"{request_id}:{r.text}")
                    except Exception as e:
                        await ws.send(f"{request_id}:ERROR {str(e)}")

                # 2. Open new WebSocket pipeline
                elif msg_type == "CONNECT_WS":
                    asyncio.create_task(handle_tornado_ws(request_id, payload, ws, local_ws))

                # 3. Stream data to Tornado
                elif msg_type == "DATA":
                    target_ws = active_ws_sessions.get(request_id)
                    if target_ws:
                        await target_ws.send(payload)

                # 4. Handle remote tab closure
                elif msg_type == "DISCONNECT_WS":
                    target_ws = active_ws_sessions.get(request_id)
                    if target_ws:
                        await target_ws.close()
                        
    except asyncio.CancelledError:
        print("[*] Agent task canceled.")
    except Exception as e:
        print(f"[-] Agent disconnected due to error: {e}")