"""
Simple WebSocket broadcast server for the web frontend.
Run: python ws_server.py
Requires: websockets (pip install websockets)
"""
import asyncio
import json
import websockets
import os
from datetime import datetime

PORT = 6789

# Message history file
MESSAGES_FILE = os.path.join(os.path.dirname(__file__), 'messages.json')

clients = set()
names = {}

# --- Message History Functions ---
def load_messages():
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_message(sender, text):
    messages = load_messages()
    messages.append({
        'sender': sender,
        'text': text,
        'timestamp': datetime.now().isoformat()
    })
    messages = messages[-1000:]
    try:
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f)
    except Exception as e:
        print(f'[!] Error saving message: {e}')

def register(ws):
    clients.add(ws)

async def unregister(ws):
    clients.discard(ws)
    name = names.pop(ws, None)
    if name:
        await broadcast({'type':'system','text':f'{name} left the chat'})

async def broadcast(obj):
    if clients:
        data = json.dumps(obj)
        await asyncio.wait([c.send(data) for c in clients])

async def handler(ws, path):
    register(ws)
    try:
        async for message in ws:
            try:
                obj = json.loads(message)
            except Exception:
                continue

            if obj.get('type') == 'join':
                names[ws] = obj.get('name','Guest')
                await broadcast({'type':'system','text':f"{names[ws]} joined the chat"})
            elif obj.get('type') == 'msg':
                name = names.get(ws,'Guest')
                text = obj.get('text','')
                save_message(name, text)
                await broadcast({'type':'msg','name':name,'text':text})
    finally:
        await unregister(ws)

def main():
    print(f'Starting WebSocket server on ws://localhost:{PORT}')
    start_server = websockets.serve(handler, '0.0.0.0', PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print('\nShutting down')

if __name__ == '__main__':
    main()
