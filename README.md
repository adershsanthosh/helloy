# Chat Application

A real-time chatting app built with Python using socket programming and Tkinter GUI.

## Features

- Real-time messaging between multiple clients
- Simple and intuitive GUI
- Username-based identification
- Connection status indicators

## Requirements

- Python 3.x
- No external dependencies (uses standard library only)

## Usage

1. Start the server:

   ```
   python server.py
   ```

2. Run client instances (can run multiple):

   ```
   python client.py
   ```

3. Enter your username when prompted

4. Type messages and press Enter to send

## Architecture

- **server.py**: Handles client connections and broadcasts messages
- **client.py**: Connects to server and provides GUI for chatting

## Web frontend (WhatsApp-like)

A simple web frontend and WebSocket server have been added to provide a WhatsApp-like UI.

Run the WebSocket server:

```
pip install -r requirements.txt
python ws_server.py
```

Serve the `web/` folder (static files) and open `web/index.html` in your browser. Example using Python's simple HTTP server from the project root:

```
cd web
python -m http.server 8000
# open http://localhost:8000 in your browser
```

The web client connects to the WebSocket server at `ws://localhost:6789` and will show a WhatsApp-like layout.
