"""Unified server: TCP chat + static file HTTP server + WebSocket broadcast for web UI."""
import socket
import threading
import asyncio
import json
import os
from datetime import datetime
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

# File transfer port
FILE_PORT = 55556

# Message history file
MESSAGES_FILE = os.path.join(os.path.dirname(__file__), 'messages.json')

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store connected TCP clients
clients = []
nicknames = {}

# --- Message History Functions ---
def load_messages():
    """Load messages from file"""
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_message(sender, text):
    """Save a message to history"""
    messages = load_messages()
    messages.append({
        'sender': sender,
        'text': text,
        'timestamp': datetime.now().isoformat()
    })
    # Keep last 1000 messages
    messages = messages[-1000:]
    try:
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f)
    except Exception as e:
        print(f"[!] Error saving message: {e}")

def get_message_history(limit=100):
    """Get recent messages"""
    messages = load_messages()
    return messages[-limit:]

def broadcast(message, sender_socket=None):
    """Send a message to all connected TCP clients except the sender"""
    # Extract sender name and message text
    sender_name = ""
    text = message
    if sender_socket in nicknames:
        sender_name = nicknames[sender_socket]
        text = message[len(sender_name) + 2:] if message.startswith(sender_name + ": ") else message
    
    # Save to history
    if sender_name and text:
        save_message(sender_name, text)
    
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

# --- File Transfer Server ---
def handle_file_transfer(client_socket, addr):
    """Handle file transfer requests"""
    print(f"[+] File transfer request from {addr}")
    try:
        # Receive file metadata
        metadata = client_socket.recv(1024).decode('utf-8')
        file_info = json.loads(metadata)
        
        filename = file_info.get('filename', 'unknown')
        filesize = file_info.get('size', 0)
        sender = file_info.get('sender', 'Unknown')
        filetype = file_info.get('type', 'image')
        
        print(f"  -> Receiving: {filename} ({filesize} bytes) from {sender}")
        
        # Save file to uploads folder
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Handle duplicate filenames
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filename = f"{base_name}_{counter}{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            counter += 1
        
        # Receive file data
        received = 0
        with open(filepath, 'wb') as f:
            while received < filesize:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
        
        print(f"  -> File saved: {filename}")
        
        # Broadcast file info to all clients
        file_msg = json.dumps({
            'type': 'file',
            'filename': filename,
            'sender': sender,
            'size': filesize,
            'filetype': filetype,
            'url': f'http://{HOST}:{HTTP_PORT}/uploads/{filename}'
        })
        broadcast(file_msg, None)
        
    except Exception as e:
        print(f"[!] File transfer error: {e}")
    finally:
        client_socket.close()

def start_file_server():
    """Start file transfer server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, FILE_PORT))
    server_socket.listen()
    print(f"[+] File transfer server started on {HOST}:{FILE_PORT}")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=handle_file_transfer, args=(client_socket, addr), daemon=True)
            thread.start()
    except Exception as e:
        print(f"[!] File server error: {e}")
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
                text = obj.get('text','')
                # Save to history
                save_message(name, text)
                await ws_broadcast({'type':'msg','name':name,'text':text})
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

# --- Static HTTP server to serve `web/` folder + API + Uploads ---
class ChatHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/messages':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            messages = get_message_history(100)
            self.wfile.write(json.dumps(messages).encode('utf-8'))
        elif self.path.startswith('/uploads/'):
            # Serve uploaded files from uploads folder
            filename = self.path[9:]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                self.path = f'/../uploads/{filename}'
            super().do_GET()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/upload':
            # Handle file upload
            content_type = self.headers.get('Content-type', '')
            if 'multipart/form-data' in content_type:
                self.handle_upload()
            else:
                self.send_error(400, 'Bad Request')
        else:
            self.send_error(404, 'Not Found')
    
    def handle_upload(self):
        """Handle file upload via HTTP"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            boundary = self.headers.get('Content-Type', '').split('boundary=')[-1]
            
            # Read the request body
            post_data = self.rfile.read(content_length)
            
            # Parse multipart data (simple parsing)
            boundary_bytes = boundary.encode('utf-8')
            parts = post_data.split(b'--' + boundary_bytes)
            
            for part in parts:
                if b'Content-Disposition: form-data; name="file"' in part:
                    # Extract filename from Content-Disposition
                    import re
                    match = re.search(b'filename="([^"]+)"', part)
                    if match:
                        filename = match.group(1).decode('utf-8')
                        
                        # Find the file data (after double newline)
                        idx = part.find(b'\r\n\r\n')
                        if idx != -1:
                            file_data = part[idx + 4:]
                            # Remove trailing \r\n
                            if file_data.endswith(b'\r\n'):
                                file_data = file_data[:-2]
                            
                            # Save file
                            filepath = os.path.join(UPLOAD_FOLDER, filename)
                            
                            # Handle duplicate filenames
                            base_name, ext = os.path.splitext(filename)
                            counter = 1
                            while os.path.exists(filepath):
                                filename = f"{base_name}_{counter}{ext}"
                                filepath = os.path.join(UPLOAD_FOLDER, filename)
                                counter += 1
                            
                            with open(filepath, 'wb') as f:
                                f.write(file_data)
                            
                            # Determine file type
                            image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
                            video_exts = ['.mp4', '.avi', '.mov', '.mkv']
                            ext = os.path.splitext(filename)[1].lower()
                            
                            if ext in image_exts:
                                filetype = 'image'
                            elif ext in video_exts:
                                filetype = 'video'
                            else:
                                filetype = 'file'
                            
                            # Broadcast file to all clients
                            file_msg = {
                                'type': 'file',
                                'filename': filename,
                                'sender': self.headers.get('X-Sender', 'Unknown'),
                                'filetype': filetype,
                                'url': f'http://{HOST}:{HTTP_PORT}/uploads/{filename}'
                            }
                            
                            # Try to broadcast via WebSocket
                            try:
                                import asyncio
                                asyncio.run(ws_broadcast(file_msg))
                            except:
                                pass
                            
                            # Send success response
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                'success': True,
                                'filename': filename,
                                'filetype': filetype,
                                'url': f'http://{HOST}:{HTTP_PORT}/uploads/{filename}'
                            }).encode('utf-8'))
                            return
            
            self.send_error(400, 'No file found')
        except Exception as e:
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

def start_http_server():
    if SimpleHTTPRequestHandler is None or ThreadingTCPServer is None:
        print('[!] http.server not available on this Python build')
        return
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    handler = partial(ChatHTTPRequestHandler, directory=web_dir)
    with ThreadingTCPServer(('0.0.0.0', HTTP_PORT), handler) as httpd:
        print(f"[+] HTTP server serving {web_dir} on http://0.0.0.0:{HTTP_PORT}")
        print(f"[+] API endpoint available at http://0.0.0.0:{HTTP_PORT}/api/messages")
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
    
    # Start File transfer server
    file_thread = threading.Thread(target=start_file_server, daemon=True)
    file_thread.start()

    # Start legacy TCP server (blocking loop) in main thread so KeyboardInterrupt works
    try:
        start_tcp_server()
    except KeyboardInterrupt:
        print('\n[!] Server shutting down...')

if __name__ == "__main__":
    main()