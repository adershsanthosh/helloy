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
