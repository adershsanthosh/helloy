"""
Chat Server - Handles client connections and broadcasts messages
"""
import socket
import threading

# Server configuration
HOST = '127.0.0.1'
PORT = 55555

# Store connected clients
clients = []
nicknames = {}

def broadcast(message, sender_socket=None):
    """Send a message to all connected clients except the sender"""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception:
                # Remove disconnected client
                remove_client(client)

def handle_client(client_socket, addr):
    """Handle individual client connections"""
    print(f"[+] New connection from {addr}")
    
    try:
        # Receive nickname
        nickname = client_socket.recv(1024).decode('utf-8')
        nicknames[client_socket] = nickname
        broadcast(f"{nickname} joined the chat!", client_socket)
        
        # Keep receiving messages
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
    """Remove a client from the chat"""
    if client_socket in clients:
        nickname = nicknames.get(client_socket, "Unknown")
        clients.remove(client_socket)
        del nicknames[client_socket]
        broadcast(f"{nickname} left the chat!")
        print(f"[-] {nickname} disconnected")

def start_server():
    """Start the chat server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    print(f"[+] Server started on {HOST}:{PORT}")
    print("[*] Waiting for connections...")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            
            # Start a new thread for each client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()