from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
import asyncio
import uuid
import uvicorn

app = FastAPI()

local_backend = None
# Store futures for HTTP requests, and direct queues/sockets for WebSockets
pending_requests = {}
browser_websockets = {}

@app.websocket("/ws")
async def websocket_gateway(ws: WebSocket):
    global local_backend

    await ws.accept()
    role = await ws.receive_text()

    if role == "local":
        local_backend = ws
        print("[+] Local backend connected")
        try:
            while True:
                msg = await ws.receive_text()
                if ":" not in msg:
                    continue

                request_id, payload = msg.split(":", 1)

                # Route back to HTTP futures
                if request_id in pending_requests:
                    pending_requests[request_id].set_result(payload)
                
                # Route back to active Browser WebSockets
                elif request_id in browser_websockets:
                    await browser_websockets[request_id].send_text(payload)

        except WebSocketDisconnect:
            print("[-] Local backend disconnected")
            local_backend = None

# Tunnel Browser WebSockets through the agent
@app.websocket("/term")
async def proxy_websocket(ws: WebSocket):
    global local_backend
    if local_backend is None:
        await ws.close(code=1011, reason="No backend connected")
        return

    await ws.accept()
    session_id = str(uuid.uuid4())
    browser_websockets[session_id] = ws

    try:
        # Notify agent to open a companion ws connection locally
        await local_backend.send_text(f"{session_id}:CONNECT_WS:/term")

        while True:
            data = await ws.receive_text()
            # Wrap browser data and send to agent
            await local_backend.send_text(f"{session_id}:DATA:{data}")
    except WebSocketDisconnect:
        if local_backend:
            await local_backend.send_text(f"{session_id}:DISCONNECT_WS")
    finally:
        browser_websockets.pop(session_id, None)

@app.api_route("/{path:path}", methods=["GET"])
async def proxy_http(path: str, request: Request):
    global local_backend
    if local_backend is None:
        return PlainTextResponse("No backend connected", status_code=503)

    request_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    pending_requests[request_id] = future

    try:
        full_path = "/" + path
        query = request.url.query
        if query:
            full_path += "?" + query

        await local_backend.send_text(f"{request_id}:HTTP:{full_path}")
        response = await asyncio.wait_for(future, timeout=30)
        return HTMLResponse(content=response)
    except asyncio.TimeoutError:
        return PlainTextResponse("Backend timeout", status_code=504)
    finally:
        pending_requests.pop(request_id, None)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)