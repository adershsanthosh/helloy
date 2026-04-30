"""Unified server: TCP chat + static file HTTP server + WebSocket broadcast for web UI."""
import socket
import threading
import asyncio
import json
import os
from functools import partial

# Optional imports for WebSocket & HTTP serving
try:
    import websockets
except Exception:
    websockets = None

try:
    from http.server import SimpleHTTPRequestHandler
    from socketserver import ThreadingTCPServer
except Exception:
    SimpleHTTPRequestHandler = None
    ThreadingTCPServer = None

# Server configuration (TCP clients)
HOST = '127.0.0.1'
PORT = 55555

# Web frontend / websocket ports
HTTP_PORT = 8000
WS_PORT = 6789

# Store connected TCP clients
clients = []
nicknames = {}

def broadcast(message, sender_socket=None):
    """Send a message to all connected TCP clients except the sender"""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception:
                remove_client(client)

def handle_client(client_socket, addr):
    print(f"[+] New TCP connection from {addr}")
    try:
        nickname = client_socket.recv(1024).decode('utf-8')
        nicknames[client_socket] = nickname
        broadcast(f"{nickname} joined the chat!", client_socket)
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    broadcast(f"{nicknames[client_socket]}: {message}", client_socket)
            except Exception:
                break
    except Exception as e:
        print(f"[!] Error handling client: {e}")
    finally:
        remove_client(client_socket)

def remove_client(client_socket):
    if client_socket in clients:
        nickname = nicknames.get(client_socket, "Unknown")
        clients.remove(client_socket)
        try:
            del nicknames[client_socket]
        except KeyError:
            pass
        broadcast(f"{nickname} left the chat!")
        print(f"[-] {nickname} disconnected")

def start_tcp_server():
    """Start the legacy TCP socket server for desktop clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[+] TCP server started on {HOST}:{PORT}")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            thread.start()
    except Exception as e:
        print(f"[!] TCP server error: {e}")
    finally:
        server_socket.close()

# --- WebSocket server (for web clients) ---
ws_clients = set()
ws_names = {}

async def ws_broadcast(obj):
    if ws_clients:
        data = json.dumps(obj)
        await asyncio.wait([c.send(data) for c in ws_clients])

async def ws_handler(ws, path):
    ws_clients.add(ws)
    try:
        async for message in ws:
            try:
                obj = json.loads(message)
            except Exception:
                continue
            if obj.get('type') == 'join':
                ws_names[ws] = obj.get('name','Guest')
                await ws_broadcast({'type':'system','text':f"{ws_names[ws]} joined the chat"})
            elif obj.get('type') == 'msg':
                name = ws_names.get(ws,'Guest')
                await ws_broadcast({'type':'msg','name':name,'text':obj.get('text','')})
    finally:
        name = ws_names.pop(ws, None)
        ws_clients.discard(ws)
        if name:
            await ws_broadcast({'type':'system','text':f"{name} left the chat"})

def start_ws_server():
    if websockets is None:
        print('[!] websockets package not installed. Web frontend websocket server will not start.')
        return
    async def _run():
        async with websockets.serve(ws_handler, '0.0.0.0', WS_PORT):
            print(f"[+] WebSocket server started on ws://0.0.0.0:{WS_PORT}")
            await asyncio.Future()  # run forever

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass

# --- Static HTTP server to serve `web/` folder ---
def start_http_server():
    if SimpleHTTPRequestHandler is None or ThreadingTCPServer is None:
        print('[!] http.server not available on this Python build')
        return
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    handler = partial(SimpleHTTPRequestHandler, directory=web_dir)
    with ThreadingTCPServer(('0.0.0.0', HTTP_PORT), handler) as httpd:
        print(f"[+] HTTP server serving {web_dir} on http://0.0.0.0:{HTTP_PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

def main():
    # Start HTTP server (static files)
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start WebSocket server
    ws_thread = threading.Thread(target=start_ws_server, daemon=True)
    ws_thread.start()

    # Start legacy TCP server (blocking loop) in main thread so KeyboardInterrupt works
    try:
        start_tcp_server()
    except KeyboardInterrupt:
        print('\n[!] Server shutting down...')

if __name__ == "__main__":
    main()